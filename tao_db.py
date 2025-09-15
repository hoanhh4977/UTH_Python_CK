import sqlite3
import random
from faker import Faker
from datetime import timedelta

fake = Faker("en_US")  # tránh sinh tiếng có dấu

# Kết nối
conn = sqlite3.connect("marketing_test.db")
cur = conn.cursor()

# Xóa bảng cũ
tables = ["Feedback","Sales","Leads","AdSpend","Customers","Campaign"]
for t in tables:
    cur.execute(f"DROP TABLE IF EXISTS {t}")

# Tạo bảng
cur.execute("""
CREATE TABLE Campaign (
    CampaignID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    Channel TEXT,
    StartDate DATE,
    EndDate DATE,
    Budget REAL
)""")

cur.execute("""
CREATE TABLE AdSpend (
    SpendID INTEGER PRIMARY KEY AUTOINCREMENT,
    CampaignID INTEGER,
    Date DATE,
    Spend REAL,
    Impressions INTEGER,
    Clicks INTEGER,
    FOREIGN KEY (CampaignID) REFERENCES Campaign(CampaignID)
)""")

cur.execute("""
CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    Age INTEGER,
    Gender TEXT,
    Location TEXT
)""")

cur.execute("""
CREATE TABLE Leads (
    LeadID INTEGER PRIMARY KEY AUTOINCREMENT,
    CampaignID INTEGER,
    CustomerID INTEGER,
    Date DATE,
    Status TEXT,
    FOREIGN KEY (CampaignID) REFERENCES Campaign(CampaignID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
)""")

cur.execute("""
CREATE TABLE Sales (
    SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID INTEGER,
    CampaignID INTEGER,
    Date DATE,
    Revenue REAL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (CampaignID) REFERENCES Campaign(CampaignID)
)""")

cur.execute("""
CREATE TABLE Feedback (
    FeedbackID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID INTEGER,
    CampaignID INTEGER,
    Rating INTEGER,
    Comment TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (CampaignID) REFERENCES Campaign(CampaignID)
)""")

# Seed Campaign
channels = ["Facebook","Google","TikTok","Email","LinkedIn"]
campaign_ids = []
for i in range(10):
    start = fake.date_between(start_date="-1y", end_date="today")
    end = start + timedelta(days=random.randint(10,60))
    cur.execute("INSERT INTO Campaign(Name,Channel,StartDate,EndDate,Budget) VALUES (?,?,?,?,?)",
                (f"Campaign {i+1}", random.choice(channels), start, end, round(random.uniform(500,5000),2)))
    campaign_ids.append(cur.lastrowid)

# Seed Customers
customer_ids = []
for i in range(100):
    cur.execute("INSERT INTO Customers(Name,Age,Gender,Location) VALUES (?,?,?,?)",
                (fake.first_name()+" "+fake.last_name(),
                 random.randint(18,60),
                 random.choice(["Male","Female"]),
                 fake.city()))
    customer_ids.append(cur.lastrowid)

# Seed AdSpend
for cid in campaign_ids:
    start = fake.date_between(start_date="-1y", end_date="today")
    for j in range(30):
        date = start + timedelta(days=j)
        spend = round(random.uniform(50,500),2)
        impressions = random.randint(1000,20000)
        clicks = random.randint(50,1000)
        cur.execute("INSERT INTO AdSpend(CampaignID,Date,Spend,Impressions,Clicks) VALUES (?,?,?,?,?)",
                    (cid, date, spend, impressions, clicks))

# Seed Leads
statuses = ["New","Contacted","Converted","Lost"]
for i in range(200):
    cur.execute("INSERT INTO Leads(CampaignID,CustomerID,Date,Status) VALUES (?,?,?,?)",
                (random.choice(campaign_ids), random.choice(customer_ids),
                 fake.date_between(start_date="-6m", end_date="today"),
                 random.choice(statuses)))

# Seed Sales
for i in range(150):
    cur.execute("INSERT INTO Sales(CampaignID,CustomerID,Date,Revenue) VALUES (?,?,?,?)",
                (random.choice(campaign_ids), random.choice(customer_ids),
                 fake.date_between(start_date="-6m", end_date="today"),
                 round(random.uniform(100,2000),2)))

# Seed Feedback
for i in range(100):
    cur.execute("INSERT INTO Feedback(CampaignID,CustomerID,Rating,Comment) VALUES (?,?,?,?)",
                (random.choice(campaign_ids), random.choice(customer_ids),
                 random.randint(1,5),
                 fake.sentence(nb_words=6)))

conn.commit()
conn.close()
print("Database marketing_test.db created successfully!")
