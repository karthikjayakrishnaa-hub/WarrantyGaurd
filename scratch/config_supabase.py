import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def main():
    load_dotenv()
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found!")
        return
        
    engine = create_engine(database_url)
    
    with engine.begin() as conn:
        print('Ensuring evidence bucket exists...')
        conn.execute(text("""
            INSERT INTO storage.buckets (id, name, public) 
            VALUES ('evidence', 'evidence', true) 
            ON CONFLICT (id) DO NOTHING;
        """))
        
        print('Creating RLS policies for storage.objects...')
        try:
            conn.execute(text("""
                CREATE POLICY "Allow public uploads to evidence"
                ON storage.objects FOR INSERT TO public WITH CHECK (bucket_id = 'evidence');
            """))
            print("Created INSERT policy")
        except Exception as e:
            print('Insert policy might already exist:', e)
            
        try:
            conn.execute(text("""
                CREATE POLICY "Allow public reads of evidence"
                ON storage.objects FOR SELECT TO public USING (bucket_id = 'evidence');
            """))
            print("Created SELECT policy")
        except Exception as e:
            print('Select policy might already exist:', e)
            
        print('Done configuring Supabase storage!')

if __name__ == '__main__':
    main()
