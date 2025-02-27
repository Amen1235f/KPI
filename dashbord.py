import pandas as pd
import dash
from dash import dcc, html
from sqlalchemy import create_engine

app = dash.Dash(__name__)

# Connexion à la base de données MySQL
engine = create_engine('mysql+mysqlconnector://root:@localhost/code')

query_commits = """
SELECT 
    r.name AS repo_name,
    ga.name AS contributor_name,
    COUNT(gc.id) AS total_commits, 
    SUM(gc.number_of_inserted_line) + SUM(gc.number_of_deleted_line) + SUM(gc.number_of_modified_line)  AS code_lines_changed, 
    SUM(gc.churn) AS total_churn,
    SUM(gc.help_others) AS total_help_others,
    SUM(gc.legacy_refactor) AS total_legacy_refactor, 
    SUM(gc.new_work) AS total_new_work, 
    SUM(gc.impact) AS total_impact, 
    SUM(gc.cyclomatic_complexity) AS total_cyclomatic_complexity,
    ga.id as contributor_id
FROM 
    repository r
LEFT JOIN git_commit gc ON r.id = gc.repository_id
LEFT JOIN git_author ga ON ga.id = gc.author_id
GROUP BY r.name, ga.name ,ga.id
ORDER BY total_commits DESC; 

"""
df_commits = pd.read_sql(query_commits, engine)

query_time_spent =""" 
    SELECT 
    r.id AS repo_id,
    ga.id AS author_id,  
    COALESCE(ga.name, 'Inconnu') AS author_name,
    MIN(gc.date) AS first_commit_date,
    MAX(gc.date) AS last_commit_date,
    DATEDIFF(MAX(gc.date), MIN(gc.date)) AS total_days_spent_contributor 
FROM 
    repository r
JOIN git_commit gc ON r.id = gc.repository_id
LEFT JOIN git_author ga ON gc.author_id = ga.id  
GROUP BY r.id, ga.id, ga.name 
ORDER BY r.id, total_days_spent_contributor DESC;

"""
df_time_spent = pd.read_sql(query_time_spent, engine)

# Calcul du total des jours passés sur tous les projets
total_days_spent = df_time_spent['total_days_spent_contributor'].sum()  

# Création des données pour le graphique "Temps passé"
time_spent_data = [{
    'x': df_time_spent['author_name'].astype(str), 
    'y': df_time_spent['total_days_spent_contributor'],  
    'type': 'bar',
    'name': 'Time Spent per Contributor'
}]

# Ajouter la barre pour le total du temps passé
time_spent_data.append({
    'x': ['Total Time Spent'],
    'y': [total_days_spent],
    'type': 'bar',
    'name': 'Total Time Spent',
    'marker': {'color': 'red'}
})
query_activity = """
SELECT 
    r.name AS repository_name,
    ga.name AS authorname,
    COUNT(gc.id) AS total_commitss,
    SUM(gc.number_of_inserted_line) + SUM(gc.number_of_deleted_line) + COALESCE(SUM(gc.number_of_modified_line), 0) AS code_lines_changes, 
    SUM(gc.churn) AS total_churns,
    SUM(gc.help_others) AS total_helps_others,
    SUM(gc.legacy_refactor) AS total_legacys_refactor, 
    SUM(gc.new_work) AS total_new_works, 
    COUNT(pr.id) AS total_pull_requests, 
    COUNT(CASE WHEN pr.status = 'merged' THEN 1 END) AS total_merged_pull_requests, 
    COUNT(CASE WHEN pr.status = 'closed' THEN 1 END) AS total_closed_pull_requests 
FROM 
    repository r
JOIN git_commit gc ON r.id = gc.repository_id
LEFT JOIN git_author ga ON gc.author_id = ga.id
LEFT JOIN pull_request pr ON r.id = pr.repository_id
GROUP BY r.id, ga.id
ORDER BY r.id, total_commitss DESC;
"""

code_instability = """
SELECT rp.id AS repository_id,
       SUM(gc.churn) AS sum_churn,
       COUNT(gc.id) as total_commits,
       SUM(gc.churn)  / COUNT(gc.id) AS total_churn_per_repository
FROM git_commit gc
JOIN repository rp ON rp.id = gc.repository_id
GROUP BY gc.repository_id
ORDER BY total_churn_per_repository DESC;
"""

df_instability = pd.read_sql(code_instability, engine)

code_instability_data = [{
    'x': df_instability['repository_id'],  
    'y': df_instability['total_churn_per_repository'],  
    'type': 'bar',
    'name': 'Code Instability (Churn per Commit)',
    'marker': {'color': 'red'},  # Red color for instability
    'hoverinfo': 'text',
    'text': df_instability.apply(lambda row: f"Total Churn: {row['sum_churn']}<br>"
                                             f"Total Commits: {row['total_commits']}<br>"
                                             f"Churn per Commit: {row['total_churn_per_repository']:.2f}",
                                 axis=1)
}]


complexity_code="""
SELECT rp.id AS repository_id,
SUM(gc.cyclomatic_complexity) AS complexity_of_code  
FROM git_commit gc
JOIN repository rp ON rp.id = gc.repository_id
GROUP BY gc.repository_id
ORDER BY complexity_of_code DESC;
"""
df_complexity=pd.read_sql(complexity_code,engine)
complexity_data=[{
    'x':df_complexity['repository_id'],
    'y':df_complexity['complexity_of_code'],
    'type':'bar',
    'name':'repository complexity',
    'marker':{'color':'purple'},
    'hoverinfo': 'text',
    'text': df_complexity.apply(lambda row: f"complexity_of_code: {row['complexity_of_code']}<br>",axis=1)
}]





df_activity = pd.read_sql(query_activity, engine)
print(df_activity.columns)

# Données pour le graphique des commits par contributeur
colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33A8', '#A833FF']  # List of distinct colors

commit_data = []

# Iterate over each repository to prepare the data for the chart
for i, repo_name in enumerate(df_commits['repo_name'].unique()):
    repo_data = df_commits[df_commits['repo_name'] == repo_name]
    
    # Append the bar chart data for each repository
    commit_data.append({
        'x': repo_data['contributor_name'],
        'y': repo_data['total_commits'],
        'type': 'bar',
        'name': f'Repo name: {repo_name} - Total Commits',
        'marker': {'color': colors[i % len(colors)]},  # Apply different color for each repository
        'hovertemplate': (
            'Contributor: %{x}<br>'  # Display contributor name
            'Total Commits: %{y}<br>'  # Display total commits
            'Code Lines Changed: %{customdata[0]}<br>'  # Display code lines changed (custom data)
            'Total Churn: %{customdata[1]}<br>'  # Display total churn (custom data)
            'Total Help Others: %{customdata[2]}<br>'  # Display total help others (custom data)
            'Total Legacy Refactor: %{customdata[3]}<br>'  # Display total legacy refactor (custom data)
            'Total Impact: %{customdata[4]}<br>'  # Display total impact (custom data)
            'Total New Work: %{customdata[5]}<br>'  # Display total new work (custom data)
            'Total Cyclomatic Complexity: %{customdata[6]}<br>'  # Display total cyclomatic complexity (custom data)
            'Contributor ID: %{customdata[7]}<br>' 
            '<extra></extra>'  # Removes the extra trace name from the hover
        ),
        'customdata': repo_data[['code_lines_changed', 'total_churn', 'total_help_others', 'total_legacy_refactor',
                                 'total_impact', 'total_new_work', 'total_cyclomatic_complexity','contributor_id']].values  # Add the extra data here
    })
activity_data=[]
activity_data = [
    {
        'x': df_activity['authorname'].astype(str),  # Contributor names
        'y': df_activity['total_commitss'],  # Total commits as primary y-axis value
        'type': 'bar',
        'name': 'Total Commits',
        'marker': {'color': 'blue'},  # Color for commits
        'hoverinfo': 'text',  # Display text on hover
        'text': df_activity.apply(lambda row: f"Commits: {row['total_commitss']}<br>"
                                              f"Lines Changed: {row['code_lines_changes']}<br>"
                                              f"Commits: {row['total_commitss']}<br>"

                                              f"Churn: {row['total_churns']}<br>"
                                              f"Help Others: {row['total_helps_others']}<br>"
                                              f"Legacy Refactor: {row['total_legacys_refactor']}<br>"
                                              f"New Work: {row['total_new_works']}<br>"
                                              f"Pull Requests: {row['total_pull_requests']}<br>"
                                              f"Merged PRs: {row['total_merged_pull_requests']}<br>"
                                              f"Closed PRs: {row['total_closed_pull_requests']}",
                            axis=1)
    }
]


# Layout de l'application Dash
app.layout = html.Div(children=[
    html.H1("Repository Commit Dashboard"),
    
    # Graphique des commits par contributeur
    dcc.Graph(
        id='commit-graph',
        figure={
            'data': commit_data,
            'layout': {
                'title': 'Total Commits per Contributor for All Repositories',
                'xaxis': {'title': 'Contributors'},
                'yaxis': {'title': 'Total Commits'},
                'barmode': 'group',  # Grouper les barres pour chaque contributeur
            }
        }
    ),
    
    # Graphique des jours passés sur le projet
    html.H1("Total Days Spent on Project"),
    dcc.Graph(
        id='duration-graph',
        figure={
            'data': time_spent_data,
            'layout': {
                'title': 'Total Days Spent on Project per Contributor',
                'xaxis': {'title': 'Contributors'},
                'yaxis': {'title': 'Time Spent (Days)'},
            }
        }
    ),
    
    html.H1("Contributor Activity"),
    dcc.Graph(
        id='activity-graph',
        figure={
            'data': activity_data,
            'layout': {
                'title': 'Total Lines Modified & Impact per Contributor',
                'xaxis': {'title': 'Contributors'},
                'yaxis': {'title': 'Value'},
            }
        }
    ),
    html.H1("code instability"),
    
    # Graphique des commits par contributeur
    dcc.Graph(
        id='churn-graph',
        figure={
            'data': code_instability_data,
            'layout': {
                'title': 'Total churn rate per  Repositories',
                'xaxis': {'title': 'repository'},
                'yaxis': {'title': 'Total churn rate'},
                'barmode': 'group',  # Grouper les barres pour chaque contributeur
            }
        }
    ),
    dcc.Graph(
        id='complexity-graph',
        figure={
            'data': complexity_data,
            'layout': {
                'title': 'Total complexity per  Repositories',
                'xaxis': {'title': 'repository'},
                'yaxis': {'title': 'Total complexity rate'},
                'barmode': 'group',  # Grouper les barres pour chaque contributeur
            }
        }
    ),

])


if __name__ == '__main__':
    app.run_server(debug=True)
