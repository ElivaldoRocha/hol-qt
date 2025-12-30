# 🏥 Gestão Onco-HOL: Painel de Indicadores de Quimioterapia

Este projeto é um **Dashboard de Inteligência Operacional** desenvolvido para a Unidade de Quimioterapia do **Hospital Ophir Loyola**. A ferramenta automatiza o processamento de planilhas estatísticas mensais, transformando dados brutos em indicadores estratégicos para suporte à tomada de decisão assistencial e administrativa.

## 🚀 Funcionalidades Principais

O sistema está organizado em 5 pilares estratégicos:

1.  **📊 Produção Detalhada:** Visualização do volume de sessões por via de acesso (EV, IM, SC, etc.) e distribuição da carga de trabalho entre enfermeiros e técnicos.
2.  **🛡️ Risco Assistencial:** Monitoramento crítico de intercorrências (extravasamentos e derramamentos) com listagem detalhada para auditoria imediata.
3.  **📈 Relatório Executivo:** Painel dinâmico com eixos duplos correlacionando Volume de Trabalho vs. Demanda de Pacientes e Índices de Segurança Real.
4.  **📝 Gerador de Parecer Técnico:** Aba dedicada à redação de pareceres narrativos com cálculos automatizados de complexidade e produtividade.
5.  **📄 Exportação em PDF:** Geração de relatórios mensais em formato PDF com cabeçalho institucional, pronto para assinatura e arquivamento.

## 🧠 Indicadores Inteligentes Calculados

- **Índice de Complexidade (MoM):** Variação percentual da carga de trabalho técnica em relação ao mês anterior.
- **Taxa de Eventos Adversos / 1k:** Métrica internacional de segurança que normaliza intercorrências por volume de procedimentos.
- **Média de Ações por Paciente:** Medida de intensidade do cuidado de enfermagem (Índice de Cuidado).
- **Previsão de Insumos:** Estimativa de consumo de dispositivos de punção venosa com margem de segurança de 20%.

## 🛠️ Tecnologias Utilizadas

- **Python 3.12+**
- **Streamlit:** Interface de usuário e Web App.
- **Pandas:** Extração e Tratamento de Dados (ETL Geográfico).
- **Plotly:** Gráficos interativos com eixos duplos e subplots.
- **FPDF:** Motor de geração de documentos PDF.
- **UV:** Gerenciamento de ambiente e dependências.

## 📂 Estrutura do Projeto

```text
HOL_QT/
├── app.py                # Ponto de entrada da aplicação Streamlit
├── src/
│   └── data_utils.py     # Lógica de ETL e processamento por subgrupos
├── assets/
│   └── img/
├── requirements.txt      # Dependências para deploy no Streamlit Cloud
└── pyproject.toml        # Configuração do projeto via UV
```

## ⚙️ Instalação e Execução Local

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/hol-qt.git
cd hol-qt
```

Crie e ative o ambiente virtual (usando uv):

```bash
uv venv
# No Windows: .venv\Scripts\activate
# No Linux/Mac: source .venv/bin/activate
```

Instale as dependências:

```bash
uv pip install -r requirements.txt
```

Execute o dashboard:

```bash
uv run streamlit run app.py
```

Desenvolvido para apoio à Unidade de Quimioterapia - Hospital Ophir Loyola.
