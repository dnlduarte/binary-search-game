# Jogo de Sorte com Pesquisa Binária
# O jogo pressupõe que o usuário usa busca binária (começando pelo 50)

import random

def jogo_pesquisa_binaria():
    number_bot = random.randint(1, 100)
    low, high = 1, 100 # alterar p comeco e fim

    print("=" * 40)
    print("  🎯 JOGO DE PESQUISA BINÁRIA (1-100)")
    print("=" * 40)
    print("Dica: use busca binária! Comece pelo 50.\n")

    while True:
        chute = int(input("Digite um número: "))

        if chute < 1 or chute > 100:
            print("⚠️  Número fora do intervalo! Digite entre 1 e 100.\n")
            continue

        if chute < number_bot:
            low = chute + 1  # atualiza limite inferior
            dica = (low + high) // 2
            print(f"📈 Muito baixo! Tente um número maior.")
            print(f"💡 Dica de busca binária: tente {dica}\n")

        elif chute > number_bot:
            high = chute - 1  # atualiza limite superior
            dica = (low + high) // 2
            print(f"📉 Muito alto! Tente um número menor.")
            print(f"💡 Dica de busca binária: tente {dica}\n")

        else:
            print(f"\n✅ Muito bom! Você acertou!")
            break


jogo_pesquisa_binaria()