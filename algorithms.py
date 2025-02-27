import pandas as pd
from sqlalchemy import create_engine
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns

engine = create_engine('mysql+mysqlconnector://root:@localhost/code')

query="""
SELECT author_id, COUNT(*) AS total_commits
FROM code_doctor_commit
GROUP BY author_id
ORDER BY total_commits DESC;
"""
query1 = """
SELECT 
  SUM(number_of_inserted_line) AS total_inserted_lines,
  SUM(number_of_deleted_line) AS total_deleted_lines,
  SUM(number_of_modified_line) AS total_modified_lines,
  CASE 
    WHEN SUM(number_of_deleted_line) = 0 THEN 0
    ELSE SUM(number_of_inserted_line) / SUM(number_of_deleted_line)
  END AS insert_delete_ratio
FROM code_doctor_commit;
"""
query2="""
SELECT 
  type, 
  COUNT(*) AS total_commits,
  SUM(number_of_inserted_line) AS total_inserted,
  SUM(number_of_deleted_line) AS total_deleted,
  AVG(number_of_inserted_line) AS avg_inserted,
  AVG(number_of_deleted_line) AS avg_deleted,
  (SUM(number_of_inserted_line) + SUM(number_of_deleted_line)) AS total_churn
FROM 
  code_doctor_commit
WHERE 
  type IS NOT NULL AND type != ''
GROUP BY 
  type
ORDER BY 
  total_commits DESC;

"""

query3="""
SELECT ga.id as author_id,
ga.name as name,
COUNT(*) as total_commits,
SUM(number_of_inserted_line) as total_lines_inserted,
SUM(number_of_deleted_line) as total_lines_deleted
FROM git_author ga
LEFT JOIN git_commit gc ON ga.id=gc.author_id
GROUP BY ga.id ,ga.name
ORDER BY total_commits DESC;

"""

query4="""
SELECT DATE(date) as commit_date,
COUNT(*) AS total_commits,
SUM(CASE WHEN msg LIKE '%fix%' THEN 1 ELSE 0 END) AS total_bug_fixes,
SUM(CASE WHEN msg LIKE '%feature%' THEN 1 ELSE 0 END) AS total_features
FROM code_doctor_commit  
WHERE 
    date >= '2023-01-01' AND date < '2024-06-01' 
GROUP BY 
    commit_date
ORDER BY 
    commit_date;
"""
query5 = """
SELECT 
    rc.contributor_id,
    COUNT(DISTINCT pr.id) AS total_pull_requests,
    COUNT(pc.id) AS total_commits
FROM 
    repository_contributor rc
LEFT JOIN 
    pull_commit pc ON rc.contributor_id = pc.code_doctor_commit_id  -- Adjust this join based on the correct column
LEFT JOIN 
    pull_request pr ON pc.pull_request_id = pr.id
GROUP BY 
    rc.contributor_id
ORDER BY 
    total_commits DESC;
"""

query6 = """
SELECT 
    rc.repository_id,
    COUNT(DISTINCT c.id) AS total_commits,
    SUM(c.number_of_inserted_line) AS total_inserted_lines,
    SUM(c.number_of_deleted_line) AS total_deleted_lines,
    SUM(c.number_of_modified_line) AS total_modified_lines,
    (SUM(c.number_of_inserted_line) + SUM(c.number_of_deleted_line)) AS total_churn,
    CASE 
        WHEN SUM(c.number_of_deleted_line) = 0 THEN 0
        ELSE SUM(c.number_of_inserted_line) / SUM(c.number_of_deleted_line)
    END AS insert_delete_ratio,
    COUNT(DISTINCT DATE(c.date)) AS commit_frequency
FROM 
    code_doctor_commit c
JOIN 
    repository_contributor rc ON c.repository_id = rc.repository_id
WHERE 
    c.date >= '2023-01-01' AND c.date < '2024-06-01'
GROUP BY 
    rc.repository_id
ORDER BY 
    total_commits DESC;
"""

fd = pd.read_sql(query6, engine)
print(fd)
plt.figure(figsize=(12, 6))

# Bar plot for total commits
plt.subplot(1, 2, 1)
sns.barplot(data=fd, x='repository_id', y='total_commits', palette='viridis')
plt.title('Total Commits per Repository')
plt.xlabel('Repository ID')
plt.ylabel('Total Commits')
plt.xticks(rotation=45)

# Bar plot for insert/delete ratio
plt.subplot(1, 2, 2)
sns.barplot(data=fd, x='repository_id', y='insert_delete_ratio', palette='magma')
plt.title('Insert/Delete Ratio per Repository')
plt.xlabel('Repository ID')
plt.ylabel('Insert/Delete Ratio')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('code_quality.png')
plt.show()

