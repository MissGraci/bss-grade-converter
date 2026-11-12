
import math
import streamlit as st
import pandas as pd

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="BSS | Conversor de Notas IB–PASB",
    page_icon="📚",
    layout="centered",
)

# ============================================================
# BOUNDARIES - BSS SL - MAY 2026 - TZ2
# ============================================================

LIMITES = {
    "Paper 1": [
        (0, 5, 1),
        (6, 11, 2),
        (12, 17, 3),
        (18, 22, 4),
        (23, 26, 5),
        (27, 31, 6),
        (32, 40, 7),
    ],
    "Paper 2": [
        (0, 5, 1),
        (6, 10, 2),
        (11, 14, 3),
        (15, 18, 4),
        (19, 21, 5),
        (22, 25, 6),
        (26, 30, 7),
    ],
    "Internal Assessment (IA)": [
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
    "Paper 1": 40,
    "Paper 2": 30,
    "Internal Assessment (IA)": 28,
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
# ESTADO DA SESSÃO
# ============================================================

if "registros_alunos" not in st.session_state:
    st.session_state.registros_alunos = []

if "ultimo_resultado" not in st.session_state:
    st.session_state.ultimo_resultado = None


# ============================================================
# FUNÇÕES
# ============================================================

def arredondar_metade_para_cima(valor):
    return math.floor(valor + 0.5)


def identificar_nota_ib(componente, pontos):
    """
    Identifica o IB Grade a partir das boundaries BSS.
    """

    for minimo, maximo, nota_ib in LIMITES[componente]:
        if minimo <= pontos <= maximo:
            return nota_ib, minimo, maximo

    raise ValueError(
        "Não foi encontrada uma faixa de nota IB."
    )


def converter_para_pasb(
    pontos,
    nota_ib,
    minimo,
    maximo
):
    """
    Interpolação linear dentro da faixa PASB correspondente.
    """

    pasb_min, pasb_max = FAIXAS_PASB[nota_ib]

    if maximo > minimo:
        posicao = (pontos - minimo) / (maximo - minimo)
    else:
        posicao = 0

    posicao = max(0.0, min(1.0, posicao))

    return (
        pasb_min
        + posicao * (pasb_max - pasb_min)
    )


def calcular_resultado(
    nome,
    componente,
    obtidos,
    possiveis
):
    """
    Converte os marks da atividade em resultado IB/PASB.
    """

    if possiveis <= 0:
        raise ValueError(
            "O total de marks precisa ser maior que zero."
        )

    if obtidos < 0 or obtidos > possiveis:
        raise ValueError(
            "Os marks obtidos devem estar entre zero "
            "e o total possível."
        )

    percentual = 100 * obtidos / possiveis

    equivalente = (
        MAX_PONTOS[componente]
        * obtidos
        / possiveis
    )

    pontos_para_faixa = min(
        MAX_PONTOS[componente],
        arredondar_metade_para_cima(equivalente)
    )

    nota_ib, minimo, maximo = identificar_nota_ib(
        componente,
        pontos_para_faixa
    )

    nota_pasb_exata = converter_para_pasb(
        pontos_para_faixa,
        nota_ib,
        minimo,
        maximo
    )

    pasb_min, pasb_max = FAIXAS_PASB[nota_ib]

    return {
        "Aluno": nome,
        "Componente": componente,
        "Marks": f"{obtidos:g}/{possiveis:g}",
        "Porcentagem (%)": round(percentual, 2),
        "Marks equivalentes": (
            f"{pontos_para_faixa}/{MAX_PONTOS[componente]}"
        ),
        "IB Grade": nota_ib,
        "IB Boundaries": (
            f"{minimo}–{maximo} "
            f"/{MAX_PONTOS[componente]}"
        ),
        "PASB Grade": arredondar_metade_para_cima(
            nota_pasb_exata
        ),
        "Faixa PASB": f"{pasb_min}–{pasb_max}",
        "PASB exata": round(nota_pasb_exata, 2),
    }


def mostrar_resultado(resultado):

    st.divider()
    st.subheader("Resultado da conversão")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Porcentagem",
            f"{resultado['Porcentagem (%)']:.2f}%"
        )

    with c2:
        st.metric(
            "IB Grade",
            resultado["IB Grade"]
        )

    with c3:
        st.metric(
            "PASB Grade",
            resultado["PASB Grade"]
        )

    st.markdown(
        f"""
**Aluno:** {resultado['Aluno']}

**Componente:** {resultado['Componente']}

**Marks obtidos:** {resultado['Marks']}

**Marks equivalentes:** {resultado['Marks equivalentes']}

**IB Boundaries:** {resultado['IB Boundaries']}

**Faixa PASB:** {resultado['Faixa PASB']}

**Nota PASB exata:** {resultado['PASB exata']:.2f}
"""
    )


# ============================================================
# ESTILO VISUAL - VERMELHO VINHO
# ============================================================

st.markdown("""
<style>

.block-container {
    max-width: 950px;
    padding-top: 2rem;
}

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

    box-shadow:
        0 8px 24px rgba(88, 28, 36, 0.20);
}

.bss-hero .eyebrow {
    font-size: 0.76rem;
    font-weight: 750;
    letter-spacing: 0.13em;
    color: #FFD9DD !important;
}

.bss-hero .heading {
    font-size: clamp(1.75rem, 4vw, 2.5rem);
    font-weight: 750;
    line-height: 1.16;

    margin: 12px 0;
    color: #FFFFFF !important;
}

.bss-hero .desc {
    color: #FFE9EC !important;
    line-height: 1.55;
    font-size: 1rem;
}

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
<div class="eyebrow">PASB · BRAZILIAN SOCIAL STUDIES · FERRAMENTA DE AVALIAÇÃO</div>
<div class="heading">Conversor de Notas<br>Brazilian Social Studies</div>
<div class="desc">Converta os marks de avaliações de BSS em notas IB e PASB e organize os resultados dos alunos em uma tabela.</div>
<span class="bss-tag">Nível SL</span>
<span class="bss-tag">Maio de 2026 · TZ2</span>
<span class="bss-tag">IB → PASB</span>
</div>
""", unsafe_allow_html=True)


# ============================================================
# INFORMAÇÕES
# ============================================================

st.info(
    "**Como funciona a calculadora:** "
    "Informe o nome do aluno, o componente da avaliação, "
    "os marks obtidos e o total possível. "
    "A calculadora transforma o resultado em uma porcentagem, "
    "converte proporcionalmente para a pontuação do componente "
    "BSS e identifica o IB Grade utilizando as boundaries "
    "de maio de 2026 (SL, TZ2). "
    "Em seguida, calcula o equivalente na escala PASB. "
    "Você pode adicionar os resultados à tabela e "
    "exportá-los para o Excel.\n\n"
    "**Observação:** As boundaries são de BSS SL. "
    "O valor exato da nota PASB é calculado por "
    "interpolação linear dentro da faixa correspondente."
)


# ============================================================
# CONFIGURAÇÃO
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
# AVALIAÇÃO INDIVIDUAL
# ============================================================

if modo == "Avaliação individual":

    st.divider()

    nome = st.text_input(
        "Nome do aluno",
        placeholder="Digite o nome do aluno"
    )

    componente = st.selectbox(
        "Componente de BSS",
        [
            "Paper 1",
            "Paper 2",
            "Internal Assessment (IA)"
        ]
    )

    st.caption(
        f"Pontuação máxima de referência: "
        f"{MAX_PONTOS[componente]} marks."
    )

    col1, col2 = st.columns(2)

    with col1:
        obtidos = st.number_input(
            "Marks obtidos pelo aluno",
            min_value=0.0,
            step=0.5,
            value=0.0
        )

    with col2:
        possiveis = st.number_input(
            "Total de marks da avaliação",
            min_value=0.5,
            step=0.5,
            value=float(MAX_PONTOS[componente])
        )

    if st.button(
        "Calcular e adicionar aluno",
        type="primary",
        use_container_width=True
    ):

        if not nome.strip():
            st.error(
                "Informe o nome do aluno antes de calcular."
            )

        else:
            try:
                resultado = calcular_resultado(
                    nome.strip(),
                    componente,
                    obtidos,
                    possiveis
                )

                st.session_state.registros_alunos.append(
                    resultado
                )

                st.session_state.ultimo_resultado = resultado

                st.success(
                    f"Resultado de {nome.strip()} "
                    "adicionado à tabela!"
                )

            except ValueError as erro:
                st.error(str(erro))


# ============================================================
# NOTA FINAL GERAL
# ============================================================

else:

    st.divider()

    nome = st.text_input(
        "Nome do aluno",
        placeholder="Digite o nome do aluno"
    )

    st.caption(
        "Informe o percentual final já ponderado. "
        "Os pesos de cada componente não foram fornecidos."
    )

    percentual = st.number_input(
        "Percentual final ponderado",
        min_value=0.0,
        max_value=100.0,
        step=0.5,
        value=0.0
    )

    if st.button(
        "Calcular e adicionar aluno",
        type="primary",
        use_container_width=True
    ):

        if not nome.strip():
            st.error(
                "Informe o nome do aluno antes de calcular."
            )

        else:
            resultado = calcular_resultado(
                nome.strip(),
                "Nota final",
                percentual,
                100.0
            )

            st.session_state.registros_alunos.append(
                resultado
            )

            st.session_state.ultimo_resultado = resultado

            st.success(
                f"Nota final de {nome.strip()} "
                "adicionada à tabela!"
            )


# ============================================================
# ÚLTIMO RESULTADO
# ============================================================

if st.session_state.ultimo_resultado is not None:

    mostrar_resultado(
        st.session_state.ultimo_resultado
    )


# ============================================================
# TABELA DE ALUNOS
# ============================================================

st.divider()

st.subheader("Tabela de notas dos alunos")

if st.session_state.registros_alunos:

    df = pd.DataFrame(
        st.session_state.registros_alunos
    )

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        f"Total de registros: {len(df)}"
    )

    # --------------------------------------------------------
    # DOWNLOAD CSV
    # --------------------------------------------------------

    csv = df.to_csv(
        index=False,
        sep=";",
        decimal=","
    ).encode("utf-8-sig")

    st.download_button(
        label="Baixar tabela para Excel (CSV)",
        data=csv,
        file_name="bss_notas_alunos.csv",
        mime="text/csv",
        use_container_width=True
    )

    # --------------------------------------------------------
    # REMOVER OU LIMPAR
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Remover último registro",
            use_container_width=True
        ):

            st.session_state.registros_alunos.pop()

            st.session_state.ultimo_resultado = None

            st.rerun()

    with col2:
        if st.button(
            "Limpar toda a tabela",
            use_container_width=True
        ):

            st.session_state.registros_alunos = []

            st.session_state.ultimo_resultado = None

            st.rerun()

else:

    st.info(
        "Nenhum aluno registrado ainda. "
        "Preencha os campos acima e clique em "
        "'Calcular e adicionar aluno'."
    )


# ============================================================
# TABELA DE BOUNDARIES
# ============================================================

with st.expander(
    "Consultar tabela de IB Boundaries BSS"
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
            "IB Grade": nota_ib,
            "Paper 1 (/40)": faixa("Paper 1"),
            "Paper 2 (/30)": faixa("Paper 2"),
            "Internal Assessment (/28)": faixa(
                "Internal Assessment (IA)"
            ),
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
# AVISO SOBRE O ARMAZENAMENTO
# ============================================================

st.warning(
    "Os registros são mantidos apenas durante esta sessão "
    "do Streamlit. Baixe a tabela em CSV antes de encerrar "
    "a sessão para não perder os resultados."
)


# ============================================================
# COPYRIGHT
# ============================================================

st.divider()

st.markdown("""
<div class="bss-footer">
© 2026 Gracielle Dias. Todos os direitos reservados.
</div>
""", unsafe_allow_html=True)
