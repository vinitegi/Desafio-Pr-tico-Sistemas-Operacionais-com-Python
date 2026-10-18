# O programa tem 3 partes:
#   1) Memória: simula FIFO e LRU (troca de páginas)
#   2) Belady:  mostra que, no FIFO, mais frames podem dar MAIS faltas
#   3) Deadlock: processos disputando recursos e travando um no outro
#
# PARTE 1 - MEMÓRIA
# ====================================================================
# Ideia geral:
#   - A "memória" é uma lista com no máximo `frames` páginas.
#   - Quando o programa pede uma página:
#       * se ela já está na lista -> HIT   (por sorte, não precisa buscar)
#       * se não está -> PAGE FAULT (precisa carregar)
#   - Se a lista estiver cheia em um PAGE FAULT, alguém precisa sair.
#     QUEM sai é o que diferencia FIFO de LRU.


def fifo(paginas, frames, mostrar=True):

    memoria = []        # as páginas que estão na memória agora
    faltas = 0          # quantos PAGE FAULT aconteceram
    hits = 0            # quantos HIT aconteceram
    trocas = 0          # quantas vezes tivemos que tirar uma página

    for pagina in paginas:

        if pagina in memoria:
            # A página já estava lá. No FIFO, não muda nada na ordem.
            hits = hits + 1
            resultado = "HIT"

        else:
            faltas = faltas + 1
            resultado = "PAGE FAULT"

            if len(memoria) >= frames:
                # Memória cheia: tira a primeira da lista (a mais antiga)
                saiu = memoria.pop(0)
                trocas = trocas + 1
                resultado = resultado + f"  (saiu a página {saiu})"

            # Coloca a nova página no final da lista
            memoria.append(pagina)

        if mostrar:
            print(f"Página {pagina:<2} -> memória {str(memoria):<16} {resultado}")

    return faltas, hits, trocas


def lru(paginas, frames, mostrar=True):

    memoria = []
    faltas = 0
    hits = 0
    trocas = 0

    for pagina in paginas:

        if pagina in memoria:
            hits = hits + 1
            resultado = "HIT"

            # Essa é a diferença do FIFO: a página foi usada agora,
            # então ela passa a ser a "mais recente" (vai pro final).
            memoria.remove(pagina)
            memoria.append(pagina)

        else:
            faltas = faltas + 1
            resultado = "PAGE FAULT"

            if len(memoria) >= frames:
                saiu = memoria.pop(0)   # a que está há mais tempo sem uso
                trocas = trocas + 1
                resultado = resultado + f"  (saiu a página {saiu})"

            memoria.append(pagina)

        if mostrar:
            print(f"Página {pagina:<2} -> memória {str(memoria):<16} {resultado}")

    return faltas, hits, trocas


def mostrar_resultado(nome, faltas, hits, trocas):
    """Mostra o resumo de um algoritmo, com as porcentagens."""
    total = faltas + hits
    taxa_faltas = faltas / total * 100
    taxa_hits = hits / total * 100

    print(f"\nResultado do {nome}:")
    print(f"  Page faults:        {faltas}")
    print(f"  Hits:               {hits}")
    print(f"  Páginas trocadas:   {trocas}")
    print(f"  Taxa de page faults: {taxa_faltas:.1f}%")
    print(f"  Taxa de hits:        {taxa_hits:.1f}%")


def comparar_fifo_lru(paginas, frames):
    """Roda os dois algoritmos na mesma sequência e compara."""
    print(f"\nSequência: {paginas}")
    print(f"Frames: {frames}")

    print("\n----- FIFO -----")
    f_faltas, f_hits, f_trocas = fifo(paginas, frames)
    mostrar_resultado("FIFO", f_faltas, f_hits, f_trocas)

    print("\n----- LRU -----")
    l_faltas, l_hits, l_trocas = lru(paginas, frames)
    mostrar_resultado("LRU", l_faltas, l_hits, l_trocas)

    print("\n----- COMPARAÇÃO -----")
    print(f"FIFO: {f_faltas} page faults")
    print(f"LRU:  {l_faltas} page faults")
    if f_faltas < l_faltas:
        print("Nessa sequência, o FIFO se saiu melhor.")
    elif l_faltas < f_faltas:
        print("Nessa sequência, o LRU se saiu melhor.")
    else:
        print("Deu empate entre FIFO e LRU.")


# PARTE 2 - ANOMALIA DE BELADY
# ====================================================================
# O normal seria pensar: "mais frames = menos page faults".
# Mas no FIFO, em algumas sequências, acontece o contrário!
# Isso se chama Anomalia de Belady.


def testar_belady(paginas, max_frames=6):
    print(f"\nSequência: {paginas}")
    print("Vamos testar o FIFO com cada quantidade de frames:\n")

    resultados = []   # guarda as faltas de cada quantidade de frames

    for frames in range(1, max_frames + 1):
        faltas, hits, trocas = fifo(paginas, frames, mostrar=False)
        resultados.append(faltas)
        print(f"  {frames} frame(s) -> {faltas} page faults")

    # Agora olhamos de dois em dois: se aumentou frames e as faltas
    # também aumentaram, achamos a anomalia.
    achou = False
    for i in range(len(resultados) - 1):
        antes = resultados[i]
        depois = resultados[i + 1]
        if depois > antes:
            achou = True
            print(f"\n>>> ANOMALIA DE BELADY! Com {i + 1} frames deu {antes} faltas,")
            print(f"    mas com {i + 2} frames (um a mais!) deu {depois} faltas.")

    if not achou:
        print("\nNão apareceu a anomalia nessa sequência.")

    # Mostra o LRU só para comparar: ele nunca sofre disso.
    print("\nPara comparar, o LRU com a mesma sequência:")
    for frames in range(1, max_frames + 1):
        faltas, hits, trocas = lru(paginas, frames, mostrar=False)
        print(f"  {frames} frame(s) -> {faltas} page faults")


# PARTE 3 - DEADLOCK
# ====================================================================

def simular_deadlock(processos):
    """
    processos: dicionário assim:  {"P1": ["A", "B"], "P2": ["B", "A"]}
    """
    dono = {}          # quem está segurando cada recurso. Ex.: {"A": "P1"}
    tem = {}           # quantos recursos cada processo já pegou
    terminou = {}      # se o processo já acabou

    for nome in processos:
        tem[nome] = 0
        terminou[nome] = False

    rodada = 0
    while True:
        rodada = rodada + 1
        print(f"\n--- Rodada {rodada} ---")
        houve_progresso = False

        for nome in processos:
            if terminou[nome]:
                continue

            precisa = processos[nome]

            # Ja pegou tudo? Então termina e devolve os recursos.
            if tem[nome] == len(precisa):
                for recurso in precisa:
                    del dono[recurso]
                terminou[nome] = True
                houve_progresso = True
                print(f"{nome}: pegou tudo, terminou e devolveu os recursos")
                continue

            # Senao, tenta pegar o próximo recurso da lista
            recurso = precisa[tem[nome]]

            if recurso not in dono:
                dono[recurso] = nome
                tem[nome] = tem[nome] + 1
                houve_progresso = True
                print(f"{nome}: pegou o recurso {recurso}")
            else:
                print(f"{nome}: quer o recurso {recurso}, mas {dono[recurso]} está usando. Esperando...")

        # Todo mundo terminou? Então não teve deadlock.
        if all(terminou.values()):
            print("\nTodos os processos terminaram. Nenhum deadlock!")
            return []

        # Ninguem avançou e ainda sobrou? usar o eadlock
        if not houve_progresso:
            print("\n*** DEADLOCK! Ninguém consegue avançar. ***")
            envolvidos = achar_ciclo(processos, dono, tem, terminou)
            print("Processos travados uns nos outros: " + ", ".join(envolvidos))
            return envolvidos


def achar_ciclo(processos, dono, tem, terminou):
    """
    Descobre QUEM esta preso no ciclo.

    Cada processo bloqueado espera por UM recurso, que está na mão de
    outro processo. Então dá para "seguir a fila":
        P1 espera P2, P2 espera P1, P1 espera P2 ...
    Se voltamos para alguém que já visitamos, achamos o ciclo.
    """
    # Monta "quem espera quem"
    espera = {}
    for nome in processos:
        if terminou[nome]:
            continue
        recurso_que_quer = processos[nome][tem[nome]]
        espera[nome] = dono[recurso_que_quer]

    # Segue a fila a partir de cada processo até repetir alguém
    for inicio in espera:
        caminho = []
        atual = inicio
        while atual in espera and atual not in caminho:
            caminho.append(atual)
            atual = espera[atual]

        if atual in caminho:
            # O ciclo é a parte do caminho a partir do primeiro repetido
            ciclo = caminho[caminho.index(atual):]
            print("Quem espera quem: " + " -> ".join(ciclo + [atual]))
            return ciclo

    return []


CENARIOS = {
    "1": ("Deadlock clássico: P1 e P2 pegam A e B em ordem inversa",
          {"P1": ["A", "B"],
           "P2": ["B", "A"]}),

    "2": ("Sem deadlock: os dois pegam A e depois B (mesma ordem)",
          {"P1": ["A", "B"],
           "P2": ["A", "B"]}),

    "3": ("Deadlock com 3 processos + P4 que não tem nada a ver com isso",
          {"P1": ["A", "B"],
           "P2": ["B", "C"],
           "P3": ["C", "A"],
           "P4": ["D"]}),
}


def menu_deadlock():
    print("\nEscolha um cenário:")
    for numero in CENARIOS:
        print(f"  {numero} - {CENARIOS[numero][0]}")
    escolha = input("Cenário: ").strip()

    if escolha not in CENARIOS:
        print("Opção inválida.")
        return

    descricao, processos = CENARIOS[escolha]
    print(f"\n{descricao}")
    for nome in processos:
        print(f"  {nome} precisa de: {processos[nome]} (nessa ordem)")
    simular_deadlock(processos)

# CONFERÊNCIA RÁPIDA
# ====================================================================
# Confere se os nossos resultados batem com os da aula.


def conferir():
    print("\n===== CONFERÊNCIA COM OS VALORES DA AULA =====")

    def checar(descricao, obtido, esperado):
        if obtido == esperado:
            print(f"[OK]     {descricao}: {obtido}")
        else:
            print(f"[ERRO]   {descricao}: veio {obtido}, esperado {esperado}")

    seq1 = [1, 2, 3, 1, 4, 2, 5, 1]
    checar("FIFO, 3 frames (faltas, hits)", fifo(seq1, 3, False)[:2], (6, 2))
    checar("LRU,  3 frames (faltas, hits)", lru(seq1, 3, False)[:2], (7, 1))

    seq2 = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    checar("FIFO sequência clássica, 3 frames", fifo(seq2, 3, False)[:2], (10, 3))
    checar("LRU  sequência clássica, 3 frames", lru(seq2, 3, False)[:2], (9, 4))

    belady = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    checar("FIFO Belady, 3 frames (faltas)", fifo(belady, 3, False)[0], 9)
    checar("FIFO Belady, 4 frames (faltas)", fifo(belady, 4, False)[0], 10)

    # Deadlock sem imprimir as rodadas: só queremos o resultado
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        d1 = simular_deadlock(CENARIOS["1"][1])
        d2 = simular_deadlock(CENARIOS["2"][1])
        d3 = simular_deadlock(CENARIOS["3"][1])
    checar("Cenário 1 trava P1 e P2", sorted(d1), ["P1", "P2"])
    checar("Cenário 2 não trava ninguém", d2, [])
    checar("Cenário 3 trava P1, P2, P3 (P4 fica de fora)", sorted(d3), ["P1", "P2", "P3"])


# MENU PRINCIPAL
# ====================================================================


def ler_numeros(texto):
    """Lê uma linha com números separados por espaço. Ex.: '1 2 3'"""
    linha = input(texto).strip()
    return [int(x) for x in linha.split()]


def main():
    # Sequência e frames padrão (a clássica do Belady)
    paginas = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    frames = 3

    while True:
        print("\n" + "=" * 50)
        print("  SIMULADOR DE SISTEMAS OPERACIONAIS")
        print("=" * 50)
        print(f"  Sequência atual: {paginas}")
        print(f"  Frames atuais:   {frames}")
        print("-" * 50)
        print("  1 - Memória: comparar FIFO e LRU")
        print("  2 - Anomalia de Belady")
        print("  3 - Deadlock")
        print("  4 - Mudar sequência de páginas e frames")
        print("  5 - Conferir se está tudo certo")
        print("  0 - Sair")

        opcao = input("\nO que você quer fazer? ").strip()

        if opcao == "1":
            comparar_fifo_lru(paginas, frames)

        elif opcao == "2":
            testar_belady(paginas)

        elif opcao == "3":
            menu_deadlock()

        elif opcao == "4":
            try:
                novas_paginas = ler_numeros("Digite as páginas separadas por espaço: ")
                novos_frames = int(input("Digite a quantidade de frames: "))
                if len(novas_paginas) == 0 or novos_frames < 1:
                    print("Precisa ter pelo menos 1 página e 1 frame. Nada foi alterado.")
                else:
                    paginas = novas_paginas
                    frames = novos_frames
                    print("Pronto, atualizado!")
            except ValueError:
                print("Opa, só dá para usar números. Nada foi alterado.")

        elif opcao == "5":
            conferir()

        elif opcao == "0":
            print("Até mais!")
            break

        else:
            print("Não entendi essa opção, tenta de novo.")


if __name__ == "__main__":
    main()