from config.openai_integration import initialize_openai, test_openai_connection

# Gebruik de gedeelde integratie module
client = initialize_openai()
# Test de verbinding
success, result = test_openai_connection(client)

if success:
    print("\nSuccesvol verbonden met de OpenAI API!")
    print(f"Voorbeeld resultaat: {result}")
else:
    print("\nFout bij verbinding met de OpenAI API.")
    print(f"Foutmelding: {result}")
