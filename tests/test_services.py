from jatai_carbono.services import buscar_fatores_por_item


if __name__ == "__main__":
    item = "Asfalto usinado a quente"

    resultado = buscar_fatores_por_item(item)

    print("INPUT:")
    print(resultado.input_item)

    print("\nCLASSIFICAÇÃO NLP:")
    print(resultado.classification)

    print("\nPRIMEIRO FATOR (se existir):")
    if resultado.factors:
        print(resultado.factors[0])
    else:
        print("Nenhum fator retornado")
