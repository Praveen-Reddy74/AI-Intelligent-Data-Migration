from db_utils import get_pg_data

# Pull only a small, representative sample
source_df = get_pg_data(
    db="insurance_source",
    query="SELECT * FROM insurance_raw",
    limit=2000
)

print("Sample shape:", source_df.shape)
print("\nSample preview:")
print(source_df.head())
