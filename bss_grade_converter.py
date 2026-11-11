
import math
import streamlit as st

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="BSS | Conversor de Notas IB–PASB",
    page_icon="📚",
    layout="centered",
)

# ============================================================
# FAIXAS DE NOTAS BSS - SL - MAIO 2026 - TZ2
# ============================================================

LIMITES = {
    "Prova 1": [
        (0, 5, 1),
        (6, 11, 2),
        (12, 17, 3),
        (18, 22, 4),
        (23, 26, 5),
        (27, 31, 6),
        (32, 40, 7),
    ],

    "Prova 2": [
        (0, 5, 1),
        (6, 10, 2),
        (11, 14, 3),
        (15, 18, 4),
        (19, 21, 5),
        (22, 25, 6),
        (26, 30, 7),
    ],

    "Avaliação interna (IA)": [
        (0, 4, 1),
        (5, 8, 2),
        (9, 11, 3),
        (12, 14, 4),
        (15, 18, 5),
        (19, 22, 6),
        (23, 28, 7),
    ],

    "Nota final": [
        (0, 15, 1),
        (16, 30, 2),
        (31, 43, 3),
        (44, 56, 4),
        (57, 67, 5),
        (68, 80, 6),
        (81, 100, 7),
    ],
}

# ============================================================
# PONTUAÇÕES MÁXIMAS
# ============================================================

MAX_PONTOS = {
    "Prova 1": 40,
    "Prova 2": 30,
    "Avaliação interna (IA)": 28,
    "Nota final": 100,
}

# ============================================================
# ESCALA PASB
# ============================================================

FAIXAS_PASB = {
    1: (0, 50),
    2: (50, 59),
    3: (60, 69),
    4: (70, 79),
    5: (80, 89),
    6: (90, 95),
    7: (96, 100),
}

# ============================================================
# FUNÇÕES DE CÁLCULO
# ============================================================

def arredondar_metade_para_cima(valor):
    """
    Arredondamento tradicional:
    92.4 -> 92
    92.5 -> 93
    """
    return math.floor(valor + 0.5)


def identificar_nota_ib(componente, pontos):
    """
    Identifica a nota IB com base nas faixas BSS.
    """
    for minimo, maximo, nota_ib in LIMITES[componente]:

        if minimo <= pontos <= maximo:
            return nota_ib, minimo, maximo

    raise ValueError(
        "Não foi encontrada uma faixa de notas correspondente."
    )


def converter_para_pasb(
    pontos,
    nota_ib,
    minimo,
    maximo
):
    """
    Calcula a nota PASB proporcionalmente dentro
    da faixa correspondente à nota IB.

    A interpolação é um método adotado nesta ferramenta.
    """

    pasb_min, pasb_max = FAIXAS_PASB[nota_ib]

    if maximo > minimo:
        posicao = (
            pontos - minimo
        ) / (
            maximo - minimo
        )
    else:
        posicao = 0

    posicao = max(
        0.0,
        min(1.0, posicao)
    )

    nota_pasb = (
        pasb_min
        + posicao * (pasb_max - pasb_min)
    )

    return nota_pasb


def exibir_resultado(
    componente,
    percentual,
    pontos_equivalentes,
    pontos_para_faixa
):
    """
    Exibe o resultado completo da conversão.
    """

    nota_ib, minimo, maximo = identificar_nota_ib(
        componente,
        pontos_para_faixa
    )

    nota_pasb = converter_para_pasb(
        pontos_para_faixa,
        nota_ib,
        minimo,
        maximo
    )

    pasb_min, pasb_max = FAIXAS_PASB[nota_ib]

    st.divider()

    st.subheader("Resultado da conversão")

    coluna_a, coluna_b, coluna_c = st.columns(3)

    with coluna_a:
        st.metric(
            "Percentual obtido",
            f"{percentual:.2f}%"
        )

    with coluna_b:
        st.metric(
            "Nota IB",
            str(nota_ib)
        )

    with coluna_c:
        st.metric(
            "Nota PASB",
            str(arredondar_metade_para_cima(nota_pasb))
        )

    st.markdown(
        f"""
**Pontuação equivalente no componente:** 
{pontos_equivalentes:.2f}/{MAX_PONTOS[componente]}

**Pontuação inteira considerada:** 
{pontos_para_faixa}/{MAX_PONTOS[componente]}

**Faixa de pontos BSS:** {minimo}–{maximo}

**Faixa de nota PASB:** {pasb_min}–{pasb_max}

**Nota PASB calculada (sem arredondar):** {nota_pasb:.2f}
"""
    )

    st.caption(
        "A nota específica dentro da faixa PASB é calculada "
        "por interpolação linear. A escala da escola informa "
        "as faixas, mas não determina essa fórmula de conversão."
    )


# ============================================================
# ESTILO VISUAL - VERMELHO VINHO
# ============================================================

st.markdown("""
<style>

/* Largura do conteúdo */

.block-container {
    max-width: 850px;
    padding-top: 2rem;
}

/* Cabeçalho principal */

.bss-hero {
    background: linear-gradient(
        120deg,
        #581C24 0%,
        #8E2937 55%,
        #B44452 100%
    );

    padding: 34px 36px;
    border-radius: 20px;
    margin-bottom: 24px;

    color: #FFFFFF !important;

    box-shadow:
        0 8px 24px rgba(88, 28, 36, 0.20);
}

/* Texto pequeno acima do título */

.bss-hero .eyebrow {
    font-size: 0.76rem;
    font-weight: 750;
    letter-spacing: 0.13em;
    color: #FFD9DD !important;
}

/* Título principal */

.bss-hero .heading {
    font-size: clamp(1.75rem, 4vw, 2.5rem);
    font-weight: 750;
    line-height: 1.16;

    margin: 12px 0;

    color: #FFFFFF !important;
}

/* Subtítulo */

.bss-hero .desc {
    color: #FFE9EC !important;
    line-height: 1.55;
    font-size: 1rem;
}

/* Etiquetas do cabeçalho */

.bss-tag {
    display: inline-block;

    margin: 13px 8px 0 0;
    padding: 6px 12px;

    border: 1px solid rgba(255,255,255,0.30);
    background: rgba(255,255,255,0.13);

    border-radius: 20px;

    font-size: 0.76rem;
    font-weight: 600;

    color: #FFFFFF !important;
}

/* Botão principal */

div.stButton > button[kind="primary"] {
    background-color: #8E2937 !important;
    color: #FFFFFF !important;
    border: 1px solid #8E2937 !important;
    border-radius: 10px !important;

    font-weight: 650 !important;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #B44452 !important;
    border-color: #B44452 !important;
    color: #FFFFFF !important;
}

/* Foco dos campos de entrada */

div[data-baseweb="input"]:focus-within {
    border-color: #B44452 !important;
}

/* Rodapé */

.bss-footer {
    text-align: center;
    color: #A78187;

    font-size: 0.82rem;
    padding: 14px 0 6px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown("""
<div class="bss-hero">
<div class="eyebrow">PASB · ESTUDOS SOCIAIS BRASILEIROS · FERRAMENTA DE AVALIAÇÃO</div>
<div class="heading">Conversor de Notas<br>Brazilian Social Studies</div>
<div class="desc">Converta a pontuação de uma avaliação de BSS em nota IB e seu equivalente na escala percentual da PASB.</div>
<span class="bss-tag">Nível SL</span>
<span class="bss-tag">Maio de 2026 · TZ2</span>
<span class="bss-tag">IB → PASB</span>
</div>
""", unsafe_allow_html=True)


# ============================================================
# EXPLICAÇÃO DA CALCULADORA
# ============================================================

st.info(
    "**Como funciona a calculadora:** "
    "Informe os pontos obtidos pelo aluno e o total de pontos "
    "da atividade. O sistema calcula o percentual alcançado "
    "e converte esse resultado para uma pontuação equivalente "
    "ao componente de Brazilian Social Studies selecionado. "
    "Em seguida, identifica a nota IB (1 a 7) utilizando "
    "as faixas de avaliação de maio de 2026 e calcula "
    "a nota correspondente na escala percentual da PASB. "
    "O valor dentro da faixa PASB é estimado proporcionalmente.\n\n"

    "**Referência utilizada:** "
    "Brazilian Social Studies – SL, maio de 2026, TZ2. "
    "As faixas HL não estão disponíveis nesta referência. "
    "Para a nota final geral, deve ser informado um percentual "
    "já ponderado, pois os pesos dos componentes não foram fornecidos."
)


# ============================================================
# CONFIGURAÇÃO DO CÁLCULO
# ============================================================

st.subheader("Configuração da avaliação")

modo = st.radio(
    "Tipo de cálculo",
    [
        "Avaliação individual",
        "Nota final geral"
    ],
    horizontal=True
)


# ============================================================
# MODO: AVALIAÇÃO INDIVIDUAL
# ============================================================

if modo == "Avaliação individual":

    st.divider()

    componente = st.selectbox(
        "Componente de BSS",
        [
            "Prova 1",
            "Prova 2",
            "Avaliação interna (IA)"
        ]
    )

    st.caption(
        f"Pontuação máxima de referência: "
        f"{MAX_PONTOS[componente]} pontos"
    )

    coluna_1, coluna_2 = st.columns(2)

    with coluna_1:

        obtidos = st.number_input(
            "Pontos obtidos pelo aluno",
            min_value=0.0,
            step=0.5,
            value=0.0
        )

    with coluna_2:

        possiveis = st.number_input(
            "Total de pontos da atividade",
            min_value=0.5,
            step=0.5,
            value=float(MAX_PONTOS[componente])
        )

    if st.button(
        "Calcular conversão",
        type="primary",
        use_container_width=True
    ):

        if obtidos > possiveis:

            st.error(
                "Os pontos obtidos não podem ultrapassar "
                "o total de pontos da atividade."
            )

        else:

            # Calcula percentual bruto

            percentual = (
                100 * obtidos / possiveis
            )

            # Converte para o total do componente BSS

            equivalente = (
                MAX_PONTOS[componente]
                * obtidos / possiveis
            )

            # Arredonda para aplicar as faixas inteiras IB

            pontos_para_faixa = min(
                MAX_PONTOS[componente],
                arredondar_metade_para_cima(equivalente)
            )

            # Mostra resultado

            exibir_resultado(
                componente,
                percentual,
                equivalente,
                pontos_para_faixa
            )


# ============================================================
# MODO: NOTA FINAL GERAL
# ============================================================

else:

    st.divider()

    st.subheader("Cálculo da nota final")

    st.caption(
        "Informe o percentual final já ponderado, "
        "entre 0 e 100%. A referência fornecida não "
        "informa os pesos de cada componente."
    )

    percentual = st.number_input(
        "Percentual final ponderado",
        min_value=0.0,
        max_value=100.0,
        step=0.5,
        value=0.0
    )

    if st.button(
        "Calcular nota final",
        type="primary",
        use_container_width=True
    ):

        pontos_para_faixa = min(
            100,
            arredondar_metade_para_cima(percentual)
        )

        exibir_resultado(
            "Nota final",
            percentual,
            percentual,
            pontos_para_faixa
        )


# ============================================================
# TABELA DE REFERÊNCIA
# ============================================================

with st.expander(
    "Consultar tabela de faixas de notas BSS"
):

    linhas = []

    for nota_ib in range(7, 0, -1):

        def faixa(componente):

            minimo, maximo, _ = next(
                item
                for item in LIMITES[componente]
                if item[2] == nota_ib
            )

            return f"{minimo}–{maximo}"

        linhas.append({
            "Nota IB": nota_ib,
            "Prova 1 (/40)": faixa("Prova 1"),
            "Prova 2 (/30)": faixa("Prova 2"),
            "IA (/28)": faixa("Avaliação interna (IA)"),
            "Nota final (%)": faixa("Nota final"),
            "PASB (%)": (
                f"{FAIXAS_PASB[nota_ib][0]}–"
                f"{FAIXAS_PASB[nota_ib][1]}"
            ),
        })

    st.dataframe(
        linhas,
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# OBSERVAÇÃO SOBRE A ESCALA PASB
# ============================================================

st.caption(
    "Observação: a tabela PASB apresenta a nota IB 1 "
    "como 0–50 e a nota IB 2 como 50–59, com sobreposição "
    "no valor 50. A classificação IB é definida antes "
    "da conversão, portanto essa sobreposição não afeta "
    "a identificação da nota IB."
)


# ============================================================
# RODAPÉ E COPYRIGHT
# ============================================================

st.divider()

st.markdown(
    """
<div class="bss-footer">
© 2026 Gracielle Dias. Todos os direitos reservados.
</div>
""",
    unsafe_allow_html=True
)
