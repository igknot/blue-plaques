from supabase import create_client, Client
from .config import settings

# Public client (anon key) - subject to RLS, used for public reads
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

# Admin client (service role key) - bypasses RLS, used for authenticated write operations
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY) if settings.SUPABASE_SERVICE_ROLE_KEY else supabase
