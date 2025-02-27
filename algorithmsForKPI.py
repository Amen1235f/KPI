import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import os
engine = create_engine('mysql+mysqlconnector://root:@localhost/code')
#def# total_commits_by_author():
   ## query = """
    #SELECT author_id, COUNT(*) as total_commits
    #FROM code_doctor_commit
    #GROUP BY author_id
    #ORDER BY total_commits DESC;
    #"""
#
    #df = pd.read_sql(query, engine)
    #print("Total Commits by Author:")
    #print(df)
#
    #results_dir = "results"
    #if not os.path.exists(results_dir):
    #    os.makedirs(results_dir)
#
    #plt.figure(figsize=(12, 6))
    #sns.barplot(data=df.head(10), x='author_id', y='total_commits', palette='viridis')
    #plt.title('Top 10 Authors by Total Commits')
    #plt.xlabel('Author ID')
    #plt.ylabel('Total Commits')
    #plt.xticks(rotation=45)
    #plt.tight_layout()
#
    #plt.savefig(f"{results_dir}/total_commits_by_author.png")
    #plt.show()
    #return df
#
#total_commits = total_commits_by_author()
#extract pull request & commits per contribuable

def analyze_pull_requests_and_commits():
    engine = create_engine('mysql+mysqlconnector://root:@localhost/code')

    query1="""
    SELECT rc.contributor_id,
    COUNT(DISTINCT pr.id) as total_pull_requests,
    COUNT(pc.id) as total_commits
    FROM  repository_contributor rc
    LEFT JOIN pull_commit pc ON  rc.contributor_id=pc.code_doctor_commit_id  
    LEFT JOIN 
        pull_request pr ON pc.pull_request_id = pr.id
    GROUP BY 
        rc.contributor_id
    ORDER BY 
        total_commits DESC;
    """
    df = pd.read_sql(query1, engine)

    print("Pull Requests and Commits per Contributor:")
    print(df)
    results_dir = "results"
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    sns.barplot(x='contributor_id', y='total_pull_requests', data=df, palette='coolwarm')
    plt.title('Total Pull Requests per Contributor')
    plt.xlabel('Contributor ID')
    plt.ylabel('Total Pull Requests')
    plt.xticks(rotation=45)

    plt.subplot(1, 2, 2)
    sns.barplot(x='contributor_id', y='total_commits', data=df, palette='viridis')
    plt.title('Total Commits per Contributor')
    plt.xlabel('Contributor ID')
    plt.ylabel('Total Commits')
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(f"{results_dir}/pull_requests_commits_per_contributor.png")
    plt.show()
total_pull_requests_commits = analyze_pull_requests_and_commits()
