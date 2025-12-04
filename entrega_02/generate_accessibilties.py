import pandas as pd
import json

# Paso 1: Parsear host_verifications y crear un CSV plano
df = pd.read_csv('datasets/listings.csv')

records = []
for _, row in df.iterrows():
    try:
        # host_verifications viene como: ['email', 'phone'] o ['phone']
        verifications = json.loads(row['host_verifications'].replace("'", '"'))
        for verification in verifications:
            records.append({
                'hosting_id': row['id'],
                'accessibility_raw': verification.strip()
            })
    except:
        pass

df_flat = pd.DataFrame(records)
df_flat.to_csv('datasets/accesibilidades_raw.csv', index=False)
print(f"{len(df_flat)} registros exportados a accesibilidades_raw.csv")

# Paso 2: Obtener accesibilidades únicas (opcional - para análisis)
def obtain_unique_accesibilidades(input_csv='datasets/accesibilidades_raw.csv', 
                                   output_csv='datasets/dim_accesibilidade.csv'):
    df = pd.read_csv(input_csv)
    unique_accesibilidades = df['accessibility_raw'].dropna().unique()
    
    df_accesibilidades = pd.DataFrame({
        'accesibilidade_id': range(1, len(unique_accesibilidades) + 1),
        'accesibilidade_name': unique_accesibilidades
    })
    
    df_accesibilidades.to_csv(output_csv, index=False)
    print(f"{len(df_accesibilidades)} accesibilidades únicas exportadas a {output_csv}")
    
    # Mostrar las accesibilidades encontradas
    print("\nAccesibilidades encontradas:")
    for _, row in df_accesibilidades.iterrows():
        print(f"  {row['accesibilidade_id']}: {row['accesibilidade_name']}")

if __name__ == "__main__":
    obtain_unique_accesibilidades()