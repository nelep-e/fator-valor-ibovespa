"""
Backtest — carteira Value (top 10) no Ibovespa: UMA carteira, comprada em 28/03/2024 e mantida até 01/07/2026
(sem rebalanceamento). Score = média dos percentis de E/P, B/M e EBIT/EV.

Fontes (gratuitas): balanços DFP da CVM + preços do Yahoo Finance.
Universo: ações do Ibovespa de jan-abr/2024 que continuam no índice hoje.
Limitação: as que saíram do índice depois de 2024 ficam fora, o que ainda favorece o resultado.
Rodar: py backtest_value_carteira_unica.py
"""
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests

# ============================== CONFIGURAÇÃO ==============================
TOP_N = 10
INICIO, FIM = "2024-03-28", "2026-07-01"  # 29/03/24 foi Sexta-feira Santa (sem pregão)
PASTA = Path(__file__).parent / "cvm"
UA = {"User-Agent": "Mozilla/5.0"}

# Ibovespa (1 classe por empresa) → CNPJ, pra ligar ticker ao balanço da CVM
UNIVERSO = {
    "VALE3": "33592510000154", "ITUB4": "60872504000123", "PETR4": "33000167000101", "AXIA3": "00001180000126",
    "SBSP3": "43776517000180", "ITSA4": "61532644000115", "EMBJ3": "07689002000189", "BBDC4": "60746948000112",
    "B3SA3": "09346601000125", "WEGE3": "84429695000111", "BPAC11": "30306294000145", "ABEV3": "07526557000100",
    "ENEV3": "04423567000121", "BBAS3": "00000000000191", "PRIO3": "10629105000168", "CPLE3": "76483817000120",
    "EQTL3": "03220438000173", "RDOR3": "06047087000139", "VBBR3": "34274233000102", "SUZB3": "16404287000155",
    "UGPA3": "33256439000139", "GGBR4": "33611500000119", "RENT3": "16670085000155", "BBSE3": "17344597000194",
    "VIVT3": "02558157000162", "RAIL3": "02387241000160", "RADL3": "61585865000151", "CSMG3": "17281106000103",
    "CMIG4": "17155730000164", "TOTS3": "53113791000122", "ENGI11": "00864214000106", "TIMS3": "02421421000111",
    "MOTV3": "02846056000197", "KLBN11": "89637490000145", "ALOS3": "05878397000132", "CXSE3": "22543331000100",
    "EGIE3": "02474103000119", "ISAE4": "02998611000104", "ASAI3": "06057223000171", "MBRF3": "03853896000140",
    "SMFT3": "07594978000178", "LREN3": "92754738000162", "SANB11": "90400888000142", "FLRY3": "60840055000131",
    "GOAU4": "92690783000109", "TAEE11": "07859971000130", "MULT3": "07816890000153", "CPFE3": "02429144000193",
    "PSSA3": "02149205000169", "CMIN3": "08902291000115", "HYPE3": "02932074000191", "CSAN3": "50746577000115",
    "IGTI11": "60543816000193", "CYRE3": "73178600000118", "BRAP4": "03847461000192", "CURY3": "08797760000183",
    "NATU3": "71673990000177", "BRAV3": "12091809000155", "AURE3": "28594234000123", "CSNA3": "33042730000104",
    "DIRR3": "16614075000100", "COGN3": "02800026000140", "POMO4": "88611835000129", "USIM5": "60894730000105",
    "YDUQ3": "08807432000110", "VIVA3": "33839910000111", "MGLU3": "47960950000121", "TEND3": "71476527000135",
    "AZZA3": "16590234000176", "MRVE3": "08343492000120", "CEAB3": "45242914000105", "VAMO3": "23373000000132",
    "HAPV3": "05197443000138", "BEEF3": "67620377000114",
}
FINANCEIRAS = {"BBAS3", "BBDC4", "ITUB4", "ITSA4", "SANB11", "BPAC11", "BBSE3", "CXSE3", "PSSA3", "BRAP4"}  # sem EBIT/EV
ACOES_POR_UNIT = {"KLBN11": 5, "ENGI11": 5, "SANB11": 2, "BPAC11": 3, "IGTI11": 3, "TAEE11": 3}
TICKER_ANTIGO = {"AXIA3": "ELET3", "EMBJ3": "EMBR3", "MBRF3": "MRFG3"}  # trocaram de código após 2024
# NATU3 fica fora: o Yahoo só tem preço dela a partir de jun/2025 e apagou o histórico do código antigo (NTCO3)

# Ibovespa de jan-abr/2024 (carteira teórica da B3), com os códigos da época
IBOV_2024 = set("""
ABEV3 ALOS3 ALPA4 ARZZ3 ASAI3 AZUL4 B3SA3 BBAS3 BBDC3 BBDC4 BBSE3 BEEF3 BHIA3 BPAC11 BRAP4 BRFS3 BRKM5 CCRO3
CIEL3 CMIG4 CMIN3 COGN3 CPFE3 CPLE6 CRFB3 CSAN3 CSNA3 CVCB3 CYRE3 DXCO3 EGIE3 ELET3 ELET6 EMBR3 ENEV3 ENGI11
EQTL3 EZTC3 FLRY3 GGBR4 GOAU4 GOLL4 HAPV3 HYPE3 IGTI11 IRBR3 ITSA4 ITUB4 JBSS3 KLBN11 LREN3 LWSA3 MGLU3 MRFG3
MRVE3 MULT3 NTCO3 PCAR3 PETR3 PETR4 PETZ3 PRIO3 RADL3 RAIL3 RAIZ4 RDOR3 RECV3 RENT3 RRRP3 SANB11 SBSP3 SLCE3
SMTO3 SOMA3 SUZB3 TAEE11 TIMS3 TOTS3 TRPL4 UGPA3 USIM5 VALE3 VAMO3 VBBR3 VIVT3 WEGE3 YDUQ3
""".split())
# código de hoje -> código de 2024, pras ações que mudaram de nome
EQUIV_2024 = {"AXIA3": "ELET3", "EMBJ3": "EMBR3", "MBRF3": "MRFG3", "MOTV3": "CCRO3", "ISAE4": "TRPL4",
              "AZZA3": "ARZZ3", "BRAV3": "RRRP3", "CPLE3": "CPLE6", "NATU3": "NTCO3"}
# fica só quem já estava no Ibovespa em 2024 (tira quem entrou depois, ex.: CSMG3, CXSE3, CURY3)
UNIVERSO = {t: c for t, c in UNIVERSO.items() if EQUIV_2024.get(t, t) in IBOV_2024}


# ============================== 1. BALANÇOS (CVM) ==============================
def carregar_dfp(ano):
    """Uma linha por empresa (CNPJ): data de entrega, lucro, PL, EBIT, dívida líquida, nº de ações."""
    arq = PASTA / f"dfp_{ano}_full.zip"
    if not arq.exists():
        PASTA.mkdir(exist_ok=True)
        url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{ano}.zip"
        arq.write_bytes(requests.get(url, timeout=300).content)
    z = zipfile.ZipFile(arq)

    def ler(parte):
        df = pd.read_csv(z.open(f"dfp_cia_aberta_{parte}{ano}.csv"), sep=";", encoding="latin-1", dtype=str)
        df["cnpj"] = df["CNPJ_CIA"].str.replace(r"\D", "", regex=True)
        return df.sort_values("VERSAO", key=lambda s: s.astype(int))  # última versão fica por último

    # todas as contas de BPA, BPP e DRE (consolidado e individual) numa tabela só
    contas = pd.concat([ler(f"{d}_{t}_").assign(tipo=t) for d in ["BPA", "BPP", "DRE"] for t in ["con", "ind"]])
    contas = contas[contas["ORDEM_EXERC"] == "ÚLTIMO"].drop_duplicates(["cnpj", "tipo", "CD_CONTA"], keep="last")
    contas["valor"] = contas["VL_CONTA"].astype(float) * np.where(contas["ESCALA_MOEDA"] == "MIL", 1000, 1)
    cod, nome = contas["CD_CONTA"], contas["DS_CONTA"].str.lower()

    def soma(filtro):  # usa o consolidado; o individual só quando não há consolidado
        x = contas[filtro].groupby(["cnpj", "tipo"])["valor"].sum().unstack().reindex(columns=["con", "ind"])
        return x["con"].combine_first(x["ind"])

    nivel2 = cod.str.fullmatch(r"\d\.\d\d")
    # PL e lucro buscados pelo NOME (em banco, a conta 2.03 é "Provisões", não PL)
    pl_total = soma(nivel2 & cod.str.startswith("2") & nome.str.contains("patrim"))
    minoritarios = soma(cod.str.fullmatch(r"2\.\d\d\.\d\d") & nome.str.contains("não controlador"))
    lucro_ctrl = soma(nome.str.contains("atribuído a sócios da empresa controladora"))
    lucro_total = soma(nivel2 & nome.str.contains(r"lucro.*do período|resultado líquido"))

    cap = ler("composicao_capital_").drop_duplicates("cnpj", keep="last").set_index("cnpj")
    acoes = cap["QT_ACAO_TOTAL_CAP_INTEGR"].astype(float) - cap["QT_ACAO_TOTAL_TESOURO"].astype(float)
    acoes = acoes.where(acoes >= 5e7, acoes * 1000)  # parte das empresas informa em milhares

    return pd.DataFrame({
        "entrega": ler("").groupby("cnpj")["DT_RECEB"].min(),  # 1ª entrega = quando ficou público
        "lucro": lucro_ctrl.combine_first(lucro_total),
        "pl": pl_total.sub(minoritarios, fill_value=0),  # PL dos controladores
        "ebit": soma(cod == "3.05"),
        "div_liq": soma(cod.isin(["2.01.04", "2.02.01"])).sub(soma(cod.isin(["1.01.01", "1.01.02"])), fill_value=0),
        "acoes": acoes,
    })


# ============================== 2. PREÇOS (Yahoo) ==============================
def baixar_precos(ticker):
    """Fechamento (ajustado por desdobramento), fechamento com dividendos, e lista de desdobramentos."""
    for t in [ticker] + ([TICKER_ANTIGO[ticker]] if ticker in TICKER_ANTIGO else []):
        sym = t if t.startswith("^") else f"{t}.SA"
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
               "?period1=1706745600&period2=1783036800&interval=1d&events=splits")
        try:
            r = requests.get(url, headers=UA, timeout=30).json()["chart"]["result"][0]
        except Exception:
            continue
        datas = pd.to_datetime(r["timestamp"], unit="s").normalize()
        p = pd.DataFrame({"close": r["indicators"]["quote"][0]["close"],
                          "adj": r["indicators"]["adjclose"][0]["adjclose"]}, index=datas)
        p = p[~p.index.duplicated(keep="last")].dropna()
        p.attrs["splits"] = [(pd.to_datetime(s["date"], unit="s"), s["numerator"] / s["denominator"])
                             for s in r.get("events", {}).get("splits", {}).values()]
        if p.index[0] <= pd.Timestamp(INICIO):
            return p
    return None


def preco(p, data, col="adj"):
    return p.loc[:data, col].iloc[-1]


# ============================== 3. RANKING VALUE ==============================
def ranking(data, precos, dfp):
    linhas = []
    for ticker, cnpj in UNIVERSO.items():
        if ticker not in precos:
            continue
        # point-in-time: balanço do ano anterior, se já entregue; senão, de 2 anos antes
        ano = next((a for a in (int(data[:4]) - 1, int(data[:4]) - 2)
                    if cnpj in dfp[a].index and dfp[a].at[cnpj, "entrega"] <= data), None)
        if ano is None:
            continue
        f = dfp[ano].loc[cnpj]
        p = precos[ticker]
        # nº de ações do balanço → base de hoje (o preço do Yahoo já está na base de hoje)
        fator = np.prod([k for dt, k in p.attrs["splits"] if dt > pd.Timestamp(f"{ano}-12-31")])
        mcap = preco(p, data, "close") * f["acoes"] * fator / ACOES_POR_UNIT.get(ticker, 1)
        if not f["pl"] > 0:
            continue
        ev = mcap + f["div_liq"]
        linhas.append({"papel": ticker, "ano_dfp": ano,
                       "E/P": f["lucro"] / mcap,
                       "B/M": f["pl"] / mcap,
                       "EBIT/EV": f["ebit"] / ev if ticker not in FINANCEIRAS and ev > 0 else np.nan})
    df = pd.DataFrame(linhas)
    df["score"] = df[["E/P", "B/M", "EBIT/EV"]].rank(pct=True).mean(axis=1)
    return df.sort_values("score", ascending=False)


# ============================== 4. BACKTEST ==============================
def main():
    print("Baixando preços...")
    uni = UNIVERSO
    precos = {t: p for t in uni if (p := baixar_precos(t)) is not None}
    ibov = baixar_precos("^BVSP")
    print(f"  {len(precos)} de {len(uni)} ações com histórico. Fora: {sorted(set(uni) - set(precos))}")
    dfp = {ano: carregar_dfp(ano) for ano in (2022, 2023)}  # carteira de mar/24 usa balanço de 2023 (ou 2022)

    # 1) monta a carteira uma única vez, com o que se sabia em 28/03/2024
    top = ranking(INICIO, precos, dfp).head(TOP_N).reset_index(drop=True)

    # 2) compra com pesos iguais e segura até o fim (preço com dividendos reinvestidos)
    dias = ibov.loc[INICIO:FIM].index  # pregões reais da B3 (o calendário do próprio Ibovespa)
    evolucao = pd.concat({t: precos[t]["adj"].reindex(dias).ffill() / preco(precos[t], INICIO)
                          for t in top["papel"]}, axis=1)
    cart = evolucao.mean(axis=1)
    ib = ibov["adj"].reindex(dias).ffill() / preco(ibov, INICIO)
    top["retorno"] = evolucao.iloc[-1].values - 1

    # 3) resultado
    print(f"\nCarteira comprada em {INICIO} e mantida até {FIM}:")
    print(top[["papel", "E/P", "B/M", "EBIT/EV", "score", "retorno"]].to_string(
        index=False, formatters={"E/P": "{:.3f}".format, "B/M": "{:.3f}".format, "EBIT/EV": "{:.3f}".format,
                                 "score": "{:.3f}".format, "retorno": "{:+.1%}".format}))
    anos = (len(dias) - 1) / 252  # anualização por pregões (padrão de mercado no Brasil)
    print()
    for nome, s in [("Carteira value", cart), ("Ibovespa", ib)]:
        total = s.iloc[-1] - 1
        print(f"{nome:15} total {total:+.1%} | ao ano {(1 + total) ** (1 / anos) - 1:+.1%} | "
              f"volatilidade {s.pct_change().std() * 252 ** 0.5:.1%} | pior queda {(s / s.cummax() - 1).min():.1%}")

    top.to_csv("carteira_unica.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")
    pd.DataFrame({"carteira": cart, "ibov": ib}).to_csv("carteira_unica_serie.csv", sep=";", decimal=",", encoding="utf-8-sig")


if __name__ == "__main__":
    main()
