import pandas as pd
import numpy as np
from fpdf import FPDF
import os

def generate_excel_template():
    with pd.ExcelWriter('dados_portico.xlsx') as writer:
        df_nos = pd.DataFrame(columns=['Nó', 'x', 'y'])
        df_nos.to_excel(writer, sheet_name='Nos', index=False)

        df_elementos = pd.DataFrame(columns=[
            'Elemento', 'Nó inicial', 'Nó final', 'E', 'I', 'A', 
            'Carga distribuída w', 'Carga concentrada P', 'Distância a'
        ])
        df_elementos.to_excel(writer, sheet_name='Elementos', index=False)

        df_cargas_nodais = pd.DataFrame(columns=['Nó', 'Fx', 'Fy', 'M'])
        df_cargas_nodais.to_excel(writer, sheet_name='Cargas_Nodais', index=False)

        df_apoios = pd.DataFrame(columns=['Nó', 'Restrições (dx,dy,theta)'])
        df_apoios.to_excel(writer, sheet_name='Apoios', index=False)

def parse_number(value):
    try:
        return float(eval(str(value).replace('^', '**')))
    except Exception:
        raise ValueError(f"Não foi possível converter o valor: {value}")

def element_stiffness_matrix(E, A, I, L):
    return np.array([
        [A*E/L, 0, 0, -A*E/L, 0, 0],
        [0, 12*E*I/L**3, 6*E*I/L**2, 0, -12*E*I/L**3, 6*E*I/L**2],
        [0, 6*E*I/L**2, 4*E*I/L, 0, -6*E*I/L**2, 2*E*I/L],
        [-A*E/L, 0, 0, A*E/L, 0, 0],
        [0, -12*E*I/L**3, -6*E*I/L**2, 0, 12*E*I/L**3, -6*E*I/L**2],
        [0, 6*E*I/L**2, 2*E*I/L, 0, -6*E*I/L**2, 4*E*I/L]
    ])

def fixed_end_force_vector(w, P, a, L):
    fe = np.zeros(6)
    fe[1] += w * L / 2
    fe[2] += w * L**2 / 12
    fe[4] += w * L / 2
    fe[5] -= w * L**2 / 12
    if P != 0:
        b = L - a
        fe[1] += P * b / L
        fe[2] += P * a * b**2 / L**2
        fe[4] += P * a / L
        fe[5] -= P * a**2 * b / L**2
    return fe

def transformation_matrix(c, s):
    T = np.zeros((6, 6))
    T[:3, :3] = [[c, s, 0], [-s, c, 0], [0, 0, 1]]
    T[3:, 3:] = T[:3, :3]
    return T

def calculate_results(data):
    nos = data['Nos']
    elementos = data['Elementos']
    cargas_nodais = data['Cargas_Nodais']
    apoios = data['Apoios']

    num_nos = len(nos)
    num_gl = num_nos * 3

    K_global = np.zeros((num_gl, num_gl))
    F_global = np.zeros(num_gl)

    node_coords = {int(row['Nó']): (row['x'], row['y']) for _, row in nos.iterrows()}

    element_forces = []

    for _, elem in elementos.iterrows():
        no_inicial = int(elem['Nó inicial'])
        no_final = int(elem['Nó final'])
        E = parse_number(elem['E'])
        I = parse_number(elem['I'])
        A = parse_number(elem['A'])
        w = parse_number(elem['Carga distribuída w']) if pd.notna(elem['Carga distribuída w']) else 0
        P = parse_number(elem['Carga concentrada P']) if pd.notna(elem['Carga concentrada P']) else 0
        a = parse_number(elem['Distância a']) if pd.notna(elem['Distância a']) else 0

        x1, y1 = node_coords[no_inicial]
        x2, y2 = node_coords[no_final]
        L = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        c = (x2 - x1) / L
        s = (y2 - y1) / L

        k_local = element_stiffness_matrix(E, A, I, L)
        T = transformation_matrix(c, s)

        k_global = T.T @ k_local @ T

        fe_local = fixed_end_force_vector(w, P, a, L)
        fe_global = T.T @ fe_local

        dof_map = [(no_inicial - 1) * 3 + i for i in range(3)] + [(no_final - 1) * 3 + i for i in range(3)]

        for i in range(6):
            for j in range(6):
                K_global[dof_map[i], dof_map[j]] += k_global[i, j]
            F_global[dof_map[i]] += fe_global[i]

        element_forces.append({
            "Elemento": elem['Elemento'],
            "No Inicial": no_inicial,
            "No Final": no_final,
            "Comprimento": L,
            "Rigidez Local": k_local,
            "Matriz Rotacao": T,
            "Forcas Nodais Equivalentes": fe_local
        })

    for _, carga in cargas_nodais.iterrows():
        no = int(carga['Nó']) - 1
        F_global[no * 3] += carga['Fx']
        F_global[no * 3 + 1] += carga['Fy']
        F_global[no * 3 + 2] += carga['M']

    prescribed_dofs = []
    for _, apoio in apoios.iterrows():
        no = int(apoio['Nó']) - 1
        restricoes = str(apoio['Restrições (dx,dy,theta)'])
        if pd.isna(restricoes) or restricoes.strip() == "":
            continue
        conditions = restricoes.split(',')
        for i, c in enumerate(['dx', 'dy', 'theta']):
            if c.strip() in conditions:
                prescribed_dofs.append(no * 3 + i)

    free_dofs = np.setdiff1d(np.arange(num_gl), prescribed_dofs)
    K_ff = K_global[np.ix_(free_dofs, free_dofs)]
    F_f = F_global[free_dofs]

    U_f = np.linalg.solve(K_ff, F_f)
    U = np.zeros(num_gl)
    U[free_dofs] = U_f

    reactions = K_global @ U - F_global

    return U, reactions, element_forces, K_global

def calculate_local_efforts(element_forces, U, nos, elementos):
    node_displacements = {int(row['Nó']): U[(int(row['Nó']) - 1) * 3:(int(row['Nó']) - 1) * 3 + 3] for _, row in nos.iterrows()}

    for elemento in element_forces:
        no_inicial = elemento['No Inicial']
        no_final = elemento['No Final']

        U_inicial = node_displacements[no_inicial]
        U_final = node_displacements[no_final]

        U_element_global = np.concatenate((U_inicial, U_final))

        T = elemento['Matriz Rotacao']

        U_element_local = T @ U_element_global

        F_local = elemento['Rigidez Local'] @ U_element_local - elemento['Forcas Nodais Equivalentes']

        elemento['Esforcos Locais'] = F_local

    return element_forces

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', '', 8)
        self.cell(0, 10, 'Resultados da Analise Estrutural', border=False, ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 6)
        self.cell(0, 10, f'Pagina {self.page_no()}', align='C')

def generate_pdf(data, U, reactions, element_forces, K_global):
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.set_font("Arial", size=6)
    pdf.add_page()

    cell_width = 15
    cell_height = 5

    pdf.set_font("Arial", 'B', 6)
    pdf.cell(0, 5, "1. Matrizes de Rigidez dos Elementos:", ln=True)
    pdf.set_font("Arial", size=6)

    for elemento in element_forces:
        pdf.set_font("Arial", 'B', 6)
        pdf.cell(0, 5, f"Elemento {elemento['Elemento']}:", ln=True)
        pdf.set_font("Arial", size=6)

        k_local = elemento['Rigidez Local']
        for row in k_local:
            for val in row:
                pdf.cell(cell_width, cell_height, f'{val:.2f}', border=1, align='C')
            pdf.ln(cell_height)

        pdf.ln(3)

    pdf.set_font("Arial", 'B', 6)
    pdf.cell(0, 5, "2. Matrizes de Rotação:", ln=True)
    pdf.set_font("Arial", size=6)

    for elemento in element_forces:
        pdf.set_font("Arial", 'B', 6)
        pdf.cell(0, 5, f"Elemento {elemento['Elemento']}:", ln=True)
        pdf.set_font("Arial", size=6)

        T = elemento['Matriz Rotacao']
        for row in T:
            for val in row:
                pdf.cell(cell_width, cell_height, f'{val:.2f}', border=1, align='C')
            pdf.ln(cell_height)

        pdf.ln(3)

    pdf.set_font("Arial", 'B', 6)
    pdf.cell(0, 5, "3. Vetores de Engastamento Perfeito (Locais):", ln=True)
    pdf.set_font("Arial", size=6)

    for elemento in element_forces:
        pdf.set_font("Arial", 'B', 6)
        pdf.cell(0, 5, f"Elemento {elemento['Elemento']}:", ln=True)
        pdf.set_font("Arial", size=6)

        fe_local = elemento['Forcas Nodais Equivalentes']
        for val in fe_local:
            pdf.cell(cell_width, cell_height, f'{val:.2f}', border=1, align='C')
        pdf.ln(cell_height)

        pdf.ln(3)

    pdf.set_font("Arial", 'B', 6)
    pdf.cell(0, 5, "4. Deslocamentos Globais:", ln=True)
    pdf.set_font("Arial", size=6)

    for i in range(len(U) // 3):
        pdf.cell(cell_width, cell_height, f'Nó {i+1}', border=1, align='C')
        pdf.cell(cell_width, cell_height, f'{U[i*3]:.4f}', border=1, align='C')
        pdf.cell(cell_width, cell_height, f'{U[i*3+1]:.4f}', border=1, align='C')
        pdf.cell(cell_width, cell_height, f'{U[i*3+2]:.4f}', border=1, align='C')
        pdf.ln(cell_height)

    pdf.ln(3)

    pdf.set_font("Arial", 'B', 6)
    pdf.cell(0, 5, "5. Esforços Locais nos Elementos:", ln=True)
    pdf.set_font("Arial", size=6)

    for elemento in element_forces:
        pdf.set_font("Arial", 'B', 6)
        pdf.cell(0, 5, f"Elemento {elemento['Elemento']}:", ln=True)
        pdf.set_font("Arial", size=6)

        esforcos_locais = elemento.get('Esforcos Locais', [])
        for val in esforcos_locais:
            pdf.cell(cell_width, cell_height, f'{val:.2f}', border=1, align='C')
        pdf.ln(cell_height)

        pdf.ln(3)

    pdf.set_font("Arial", 'B', 6)
    pdf.cell(0, 5, "6. Reações nos Apoios:", ln=True)
    pdf.set_font("Arial", size=6)

    for i, reaction in enumerate(reactions):
        pdf.cell(cell_width, cell_height, f'GL {i+1}', border=1, align='C')
        pdf.cell(cell_width, cell_height, f'{reaction:.2f}', border=1, align='C')
        pdf.ln(cell_height)

    pdf.ln(3)

    pdf.set_font("Arial", 'B', 6)
    pdf.cell(0, 5, "7. Matriz de Rigidez Global:", ln=True)
    pdf.set_font("Arial", size=6)

    for row in K_global:
        for val in row:
            pdf.cell(cell_width, cell_height, f'{val:.2f}', border=1, align='C')
        pdf.ln(cell_height)

    pdf.ln(3)

    pdf.set_font("Arial", 'B', 6)
    pdf.cell(0, 5, "8. Vetor Global de Forças Nodais Equivalentes:", ln=True)
    pdf.set_font("Arial", size=6)

    F_lep = np.zeros(len(U))
    for elemento in element_forces:
        no_inicial = elemento['No Inicial'] - 1
        no_final = elemento['No Final'] - 1
        dof_map = [(no_inicial * 3 + i) for i in range(3)] + [(no_final * 3 + i) for i in range(3)]

        T = elemento['Matriz Rotacao']
        fe_local = elemento['Forcas Nodais Equivalentes']
        fe_global = T.T @ fe_local

        for idx, dof in enumerate(dof_map):
            F_lep[dof] += fe_global[idx]

    for i, val in enumerate(F_lep):
        pdf.cell(cell_width, cell_height, f'GL {i+1}', border=1, align='C')
        pdf.cell(cell_width, cell_height, f'{val:.2f}', border=1, align='C')
        pdf.ln(cell_height)

    pdf.output("resultados_analise.pdf")
    
def main():
    data = {
        "Nos": pd.read_excel('dados_portico.xlsx', sheet_name="Nos"),
        "Elementos": pd.read_excel('dados_portico.xlsx', sheet_name="Elementos"),
        "Cargas_Nodais": pd.read_excel('dados_portico.xlsx', sheet_name="Cargas_Nodais"),
        "Apoios": pd.read_excel('dados_portico.xlsx', sheet_name="Apoios"),
    }

    U, reactions, element_forces, K_global = calculate_results(data)
    element_forces = calculate_local_efforts(element_forces, U, data['Nos'], data['Elementos'])
    generate_pdf(data, U, reactions, element_forces, K_global)
    print("Resultados salvos em 'resultados_analise.pdf'")

if __name__ == "__main__":
    main()
