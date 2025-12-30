import re

import pandas as pd


def process_hospital_data(file):
    if hasattr(file, "name") and file.name.endswith(".csv"):
        df_raw = pd.read_csv(file, header=None)
    else:
        df_raw = pd.read_excel(file, header=None)

    df_raw = df_raw.iloc[:, :13]
    meses_oficiais = [
        "JAN.",
        "FEV.",
        "MAR.",
        "ABR.",
        "MAI.",
        "JUN.",
        "JUL.",
        "AGO.",
        "SET.",
        "OUT.",
        "NOV.",
        "DEZ.",
    ]

    indices = {}
    for i, row in df_raw.iterrows():
        val = str(row[0]).strip().upper()
        if "ESTATÍSTICA DA QUIMIOTERAPIA –  PROCEDIMENTOS" in val:
            indices["G1"] = i
        elif "SESSÕES REALIZADAS NA QUIMIOTERAPIA" in val:
            indices["G2"] = i
        elif "PROCEDIMENTOS REALIZADOS PELOS PROFISSIONAL ENFERMEIRO" in val:
            indices["G3"] = i
        elif "PROCEDIMENTOS REALIZADOS PELOS PROFISSIONAL TÉCNICO DE ENFERMAGEM" in val:
            indices["G4"] = i

    def limpar_procedimento(nome):
        nome = str(nome).strip()
        substituicoes = {
            "QUANTIDADE DE": "Qtd.",
            "QUANTIDADE": "Qtd.",
            "INJEÇÕES": "Inj.",
            "INJEÇÃO": "Inj.",
            "QUIMIOTERAPIA": "QT",
        }
        for k, v in substituicoes.items():
            nome = re.sub(rf"\b{k}\b", v, nome, flags=re.IGNORECASE)
        return nome

    def extrair_fatia(inicio, fim, subgrupo, profissional=None):
        fatia = df_raw.iloc[inicio:fim].copy()
        fatia.columns = ["Procedimento"] + meses_oficiais
        fatia_longa = fatia.melt(
            id_vars=["Procedimento"], var_name="Mes", value_name="Quantidade"
        )
        fatia_longa["Quantidade"] = (
            pd.to_numeric(fatia_longa["Quantidade"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

        # --- CORREÇÃO AQUI ---
        # Antes apagávamos tudo com "TOTAL". Agora apagamos APENAS os rodapés específicos
        # Isso preserva a linha "TOTAL DE PACIENTES..."
        fatia_longa = fatia_longa[fatia_longa["Quantidade"] > 0]
        termos_para_remover = [
            "TOTAL DE PROCEDIMENTOS",
            "SESSÕES REALIZADAS",
            "PROCEDIMENTOS REALIZADOS",
        ]
        for termo in termos_para_remover:
            fatia_longa = fatia_longa[
                ~fatia_longa["Procedimento"].str.contains(termo, na=False, case=False)
            ]
        # ----------------------

        fatia_longa["Procedimento_Original"] = fatia_longa["Procedimento"]
        fatia_longa["Procedimento"] = fatia_longa["Procedimento"].apply(
            limpar_procedimento
        )
        fatia_longa["Subgrupo"] = subgrupo
        fatia_longa["Profissional"] = profissional if profissional else "N/A"
        return fatia_longa

    g1 = extrair_fatia(indices["G1"] + 1, indices["G2"], "Estatísticas Gerais")
    g2 = extrair_fatia(indices["G2"] + 1, indices["G3"], "Sessões Realizadas")
    g3 = extrair_fatia(indices["G3"] + 1, indices["G4"], "Produção", "Enfermeiro")

    try:
        fim_tecnico = df_raw[
            df_raw[0].str.contains("TOTAL.*TECNICO", na=False, case=False, regex=True)
        ].index[0]
    except:
        fim_tecnico = len(df_raw)
    g4 = extrair_fatia(
        indices["G4"] + 1, fim_tecnico, "Produção", "Técnico de Enfermagem"
    )

    df_final = pd.concat([g1, g2, g3, g4], ignore_index=True)
    df_final["Procedimento_Curto"] = df_final["Procedimento"].apply(
        lambda x: x[:35] + "..." if len(x) > 35 else x
    )
    df_final["Mes"] = df_final["Mes"].str.strip()

    return df_final
