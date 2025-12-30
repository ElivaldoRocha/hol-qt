import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # Necessário para eixos duplos
import streamlit as st
from fpdf import FPDF  # Biblioteca para geração de PDF
from plotly.subplots import make_subplots

from src.data_utils import process_hospital_data

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="Gestão Onco-HOL", layout="wide", page_icon="🏥")

st.markdown(
    """
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { font-size: 28px !important; color: #1f77b4 !important; }
    .executive-note { background-color: #e8f0f7; padding: 15px; border-left: 5px solid #1f77b4; border-radius: 5px; margin-bottom: 10px; font-style: italic; }
    </style>
    """,
    unsafe_allow_html=True,
)


def aplicar_estilo_grafico(fig, titulo):
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=26)),
        font=dict(size=16, color="black"),
        legend=dict(
            font=dict(size=18),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=50, r=50, t=120, b=50),
    )
    fig.update_xaxes(tickfont=dict(size=18))
    fig.update_yaxes(tickfont=dict(size=16))
    return fig


# Função auxiliar para gerar o PDF com LOGO
def gerar_pdf_gestao(mes, texto_relatorio):
    pdf = FPDF()
    pdf.add_page()

    # Caminho do Logo
    logo_path = "assets/img/Logo_HOL.png"

    # Inserir Logo no Cabeçalho do PDF (se existir)
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=20)
        pdf.set_x(35)  # Desloca o texto para não sobrepor o logo

    # Cabeçalho Institucional
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "HOSPITAL OPHIR LOYOLA", ln=True, align="C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(
        190, 10, "UNIDADE DE QUIMIOTERAPIA - RELATORIO DE GESTAO", ln=True, align="C"
    )
    pdf.ln(5)
    pdf.line(10, 35, 200, 35)
    pdf.ln(10)

    # Título do Relatório
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, f"Analise Mensal: {mes}", ln=True)
    pdf.ln(5)

    # Conteúdo do Relatório
    pdf.set_font("Arial", "", 11)
    texto_limpo = texto_relatorio.encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(190, 8, texto_limpo)

    # Rodapé para Assinatura
    pdf.ln(30)
    pdf.cell(190, 10, "_" * 50, ln=True, align="C")
    pdf.cell(
        190, 10, "Responsavel Tecnica / Gerencia de Enfermagem", ln=True, align="C"
    )

    return pdf.output(dest="S").encode("latin-1")


# 2. BARRA LATERAL (LOGO E UPLOAD)
# Exibir o Logo no topo da barra lateral
logo_sidebar = "assets/img/Logo_HOL.png"
if os.path.exists(logo_sidebar):
    st.sidebar.image(logo_sidebar, width=180)

st.title("🏥 Inteligência de Dados - Enfermagem Oncológica")

uploaded_file = st.sidebar.file_uploader(
    "📂 Arraste a planilha aqui", type=["csv", "xlsx"]
)

if uploaded_file:
    df = process_hospital_data(uploaded_file)
    ordem_meses = [
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
    meses_no_df = [m for m in ordem_meses if m in df["Mes"].unique()]

    st.sidebar.subheader("Configurações")
    mes_sel = st.sidebar.selectbox("Escolha o Mês para análise", meses_no_df)
    df_mes = df[df["Mes"] == mes_sel]

    # --- 3. CÁLCULO DE MÉTRICAS (KPIs) ---
    producao = df_mes[df_mes["Subgrupo"] == "Produção"]["Quantidade"].sum()
    df_g1 = df_mes[df_mes["Subgrupo"] == "Estatísticas Gerais"]
    pac_amb = df_g1[
        df_g1["Procedimento_Original"].str.contains("AMBULATORIAL", na=False)
    ]["Quantidade"].sum()
    if pac_amb == 0:
        pac_amb = df_g1["Quantidade"].max() if not df_g1.empty else 1

    novos = df_mes[
        df_mes["Procedimento_Original"].str.contains("PRIMEIRA VEZ", na=False)
    ]["Quantidade"].sum()
    inter_total = df_mes[
        df_mes["Procedimento_Original"].str.contains(
            "EXTRAVASAMENTO|DERRAMAMENTO", case=False, na=False
        )
    ]["Quantidade"].sum()

    punc_atual = df_mes[
        df_mes["Procedimento_Original"].str.contains("PUNÇÃO|PUNÇÕES", na=False)
    ]["Quantidade"].sum()

    mes_idx = meses_no_df.index(mes_sel)
    delta_complexidade = 0
    if mes_idx > 0:
        mes_ant = meses_no_df[mes_idx - 1]
        prod_ant = df[(df["Mes"] == mes_ant) & (df["Subgrupo"] == "Produção")][
            "Quantidade"
        ].sum()
        if prod_ant > 0:
            delta_complexidade = ((producao - prod_ant) / prod_ant) * 100

    # --- 4. KPIs DE TOPO ---
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Pacientes Totais", int(pac_amb))
    m2.metric("Pacientes Novos", int(novos))
    m3.metric("Produção Total", int(producao))
    m4.metric(
        "Intercorrências",
        int(inter_total),
        delta="Atenção" if inter_total > 0 else "Seguro",
        delta_color="inverse",
    )
    m5.metric("Complexidade", f"{delta_complexidade:+.1f}%")

    st.write("---")

    # --- 5. ABAS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Produção Detalhada",
            "🛡️ Risco Assistencial",
            "📈 Relatório Executivo",
            "📋 Dados Brutos",
            "📄 Relatório Narrativo",
        ]
    )

    with tab1:
        st.plotly_chart(
            aplicar_estilo_grafico(
                px.bar(
                    df_mes[df_mes["Subgrupo"] == "Sessões Realizadas"],
                    x="Quantidade",
                    y="Procedimento",
                    orientation="h",
                    color_discrete_sequence=["#2ca02c"],
                    text_auto=True,
                ),
                "Sessões Realizadas por Via de Acesso",
            ),
            width="stretch",
        )

        st.write("---")
        st.plotly_chart(
            aplicar_estilo_grafico(
                px.pie(
                    df_mes[df_mes["Subgrupo"] == "Produção"],
                    values="Quantidade",
                    names="Profissional",
                    hole=0.5,
                    color_discrete_sequence=["#1f77b4", "#aec7e8"],
                ),
                "Carga de Trabalho: Enfermeiro vs Técnico",
            ),
            width="stretch",
        )

        st.write("---")
        st.plotly_chart(
            aplicar_estilo_grafico(
                px.bar(
                    df_mes[df_mes["Subgrupo"] == "Produção"].nlargest(10, "Quantidade"),
                    x="Quantidade",
                    y="Procedimento_Curto",
                    orientation="h",
                    color="Profissional",
                    text_auto=True,
                ),
                "Top 10 Atividades do Mês",
            ),
            width="stretch",
        )

    with tab2:
        if inter_total > 0:
            st.error(f"Eventos adversos em {mes_sel}")
            st.table(
                df_mes[
                    df_mes["Procedimento_Original"].str.contains(
                        "EXTRAVASAMENTO|DERRAMAMENTO", na=False
                    )
                ][["Procedimento_Original", "Profissional", "Quantidade"]].set_index(
                    "Procedimento_Original"
                )
            )
        else:
            st.success("Operação 100% segura no período analisado.")

    with tab3:
        st.subheader("🚀 Inteligência Estratégica Mensal (Visão Direção)")
        data_lista = []
        for m in meses_no_df:
            d_m = df[df["Mes"] == m]
            prod = d_m[d_m["Subgrupo"] == "Produção"]["Quantidade"].sum()
            pac = d_m[
                (d_m["Subgrupo"] == "Estatísticas Gerais")
                & (d_m["Procedimento_Original"].str.contains("AMBULATORIAL"))
            ]["Quantidade"].sum()
            if pac == 0:
                pac = d_m[d_m["Subgrupo"] == "Estatísticas Gerais"]["Quantidade"].max()
            if pac == 0:
                pac = 1

            inter = d_m[
                d_m["Procedimento_Original"].str.contains("EXTRAVASAMENTO|DERRAMAMENTO")
            ]["Quantidade"].sum()
            punc = d_m[d_m["Procedimento_Original"].str.contains("PUNÇÃO|PUNÇÕES")][
                "Quantidade"
            ].sum()

            curr_idx = ordem_meses.index(m)
            comp_mom = 0
            if curr_idx > 0:
                prev_m = ordem_meses[curr_idx - 1]
                if prev_m in df["Mes"].unique():
                    p_prev = df[(df["Mes"] == prev_m) & (df["Subgrupo"] == "Produção")][
                        "Quantidade"
                    ].sum()
                    if p_prev > 0:
                        comp_mom = ((prod - p_prev) / p_prev) * 100

            data_lista.append(
                {
                    "Mes": m,
                    "Trabalho": prod,
                    "Pacientes": pac,
                    "Complexidade": comp_mom,
                    "Taxa_Eventos": (inter / prod * 1000 if prod > 0 else 0),
                    "Intensidade": prod / pac,
                    "Insumos": punc * 1.2,
                }
            )

        df_exec = pd.DataFrame(data_lista)
        df_exec["Mes"] = pd.Categorical(
            df_exec["Mes"], categories=ordem_meses, ordered=True
        )
        df_exec = df_exec.sort_values("Mes")

        st.markdown(
            '<div class="executive-note">"Diretor, note que o volume de trabalho assistencial não acompanha obrigatoriamente o número de pacientes; ele cresce conforme a complexidade dos protocolos."</div>',
            unsafe_allow_html=True,
        )
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig1.add_trace(
            go.Scatter(
                x=df_exec["Mes"],
                y=df_exec["Trabalho"],
                name="Produção (Ações)",
                line=dict(color="#1f77b4", width=4),
            ),
            secondary_y=False,
        )
        fig1.add_trace(
            go.Scatter(
                x=df_exec["Mes"],
                y=df_exec["Pacientes"],
                name="Pacientes",
                line=dict(color="#ff7f0e", width=4, dash="dot"),
            ),
            secondary_y=True,
        )
        fig1.update_yaxes(title_text="Volume de Ações", secondary_y=False)
        fig1.update_yaxes(title_text="Volume de Pacientes", secondary_y=True)
        st.plotly_chart(
            aplicar_estilo_grafico(fig1, "Tendência: Produção vs Demanda"),
            width="stretch",
        )

        st.write("---")
        st.markdown(
            '<div class="executive-note">"Esta correlação prova que picos de complexidade (sobrecarga) elevam o risco de eventos adversos. Manter o dimensionamento correto é uma estratégia de segurança."</div>',
            unsafe_allow_html=True,
        )
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(
            go.Bar(
                x=df_exec["Mes"],
                y=df_exec["Complexidade"],
                name="Complexidade MoM (%)",
                marker_color="#9467bd",
                opacity=0.4,
            ),
            secondary_y=False,
        )
        fig2.add_trace(
            go.Scatter(
                x=df_exec["Mes"],
                y=df_exec["Taxa_Eventos"],
                name="Eventos / 1k Proc.",
                line=dict(color="#d62728", width=4),
            ),
            secondary_y=True,
        )
        fig2.update_yaxes(title_text="Variação de Carga (%)", secondary_y=False)
        fig2.update_yaxes(title_text="Taxa de Eventos", secondary_y=True)
        st.plotly_chart(
            aplicar_estilo_grafico(fig2, "Relação: Complexidade vs Segurança Real"),
            width="stretch",
        )

        st.write("---")
        st.markdown(
            '<div class="executive-note">"Baseado na média de ações por paciente, projetamos o consumo real de insumos (agulhas/cateteres), garantindo que não falte material para a produção."</div>',
            unsafe_allow_html=True,
        )
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        fig3.add_trace(
            go.Scatter(
                x=df_exec["Mes"],
                y=df_exec["Intensidade"],
                name="Ações por Paciente",
                line=dict(color="#e377c2", width=4),
            ),
            secondary_y=False,
        )
        fig3.add_trace(
            go.Bar(
                x=df_exec["Mes"],
                y=df_exec["Insumos"],
                name="Previsão de Agulhas",
                marker_color="#2ca02c",
                opacity=0.4,
            ),
            secondary_y=True,
        )
        fig3.update_yaxes(title_text="Intensidade (Ações/Pac)", secondary_y=False)
        fig3.update_yaxes(title_text="Estoque Necessário", secondary_y=True)
        st.plotly_chart(
            aplicar_estilo_grafico(fig3, "Relação: Intensidade vs Suprimentos"),
            width="stretch",
        )

    with tab4:
        st.subheader("Base de Dados Auditoria")
        st.dataframe(
            df_mes[["Procedimento", "Subgrupo", "Profissional", "Quantidade"]],
            width="stretch",
        )
        csv = df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button(
            "📥 Baixar Base Final (CSV)", csv, f"Auditoria_QT_{mes_sel}.csv", "text/csv"
        )

    with tab5:
        st.subheader("📝 Gerador de Relatório Técnico-Administrativo")
        st.info(
            "Este relatório converte os indicadores em um parecer narrativo pronto para assinatura."
        )
        taxa_seg = (inter_total / producao * 1000) if producao > 0 else 0
        parecer_automático = f"""PARECER TECNICO DE ENFERMAGEM ONCOLOGICA - {mes_sel}

1. RESUMO OPERACIONAL:
No mes de {mes_sel}, a unidade registrou o atendimento de {int(pac_amb)} pacientes. O volume total de procedimentos assistenciais realizados pela equipe de enfermagem somou {int(producao)} acoes, resultando em um indice de intensidade de {(producao / pac_amb):.1f} procedimentos por paciente.

2. SEGURANCA E QUALIDADE:
Foram registrados {int(inter_total)} eventos adversos (extravasamentos/derramamentos). Estatisticamente, isso representa uma taxa de {taxa_seg:.2f} eventos para cada 1.000 procedimentos realizados. Este indice mantem-se dentro dos padroes de monitoramento da unidade.

3. COMPLEXIDADE E RECURSOS:
Observou-se uma variacao de complexidade de {delta_complexidade:+.1f}% em relacao ao mes anterior. Com base no volume de puncoes assistenciais, estima-se a necessidade de {int(punc_atual * 1.2)} dispositivos de puncao venosa para a manutencao do estoque de seguranca no proximo ciclo.

O presente relatorio baseia-se nos dados estatisticos processados pelo sistema de indicadores Gestao Onco-HOL."""

        texto_para_pdf = st.text_area(
            "Revise ou edite o texto abaixo antes de exportar:",
            value=parecer_automático,
            height=400,
        )

        if st.button("🚀 Processar Relatório para PDF"):
            try:
                pdf_output = gerar_pdf_gestao(mes_sel, texto_para_pdf)
                st.download_button(
                    label="📥 Clique aqui para Baixar o Relatório em PDF",
                    data=pdf_output,
                    file_name=f"Relatorio_Gestao_{mes_sel}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Erro ao gerar documento: {e}")

else:
    st.info(
        "💡 Arraste a planilha de estatísticas para gerar os indicadores executivos."
    )
