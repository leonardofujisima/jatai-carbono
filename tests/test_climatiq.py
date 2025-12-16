from jatai_carbono.climatiq_client import buscar_fatores_climatiq

print("Teste termo amplo:")
print(buscar_fatores_climatiq("grid mix")[:1])

print("\nTeste termo específico:")
print(buscar_fatores_climatiq("hot mix asphalt"))
