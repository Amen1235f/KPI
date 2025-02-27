import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns

def commits_per_month(file_path):
    # Lire le fichier SQL
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            sql_content = file.read()
    except FileNotFoundError:
        print(f"Le fichier {file_path} n'a pas été trouvé.")
        return

    # Extraire les dates de commits
    pattern = r"INSERT INTO `code_doctor_commit`.*?\((\d+),.*?,.*?,.*?,.*?,'(\d{4}-\d{2}-\d{2})'"
    matches = re.findall(pattern, sql_content)

    if not matches:
        print("Aucune date de commit trouvée.")
        return

    # Créer un DataFrame avec les dates
    df = pd.DataFrame(matches, columns=['commit_id', 'commit_date'])
    df['commit_date'] = pd.to_datetime(df['commit_date'])

    # Groupement par mois et comptage
    commits_by_month = df.groupby(df['commit_date'].dt.to_period('M')).size().reset_index(name='total_commits')

    # Visualisation
    if not commits_by_month.empty:
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=commits_by_month, x='commit_date', y='total_commits', marker='o')
        plt.title("Nombre de commits par mois")
        plt.xlabel("Date")
        plt.ylabel("Total Commits")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print("Aucun commit à afficher.")

# Appel de la fonction
commits_per_month("code-doctor-dump.sql")
