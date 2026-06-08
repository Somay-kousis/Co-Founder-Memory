# memory/supabase_store.py
import os
from typing import Optional, Tuple, Any, Iterable
from langgraph.store.base import BaseStore, Item, Op, Result, GetOp, PutOp, SearchOp
from supabase import create_client, Client

class SupabaseStore(BaseStore):
    """
    Custom LangGraph Store that persists the PermanentMemoryProfile in a Supabase table.
    """
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        super().__init__()
        url = supabase_url or os.getenv("SUPABASE_URL")
        key = supabase_key or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        
        self.client: Optional[Client] = None
        if url and key:
            try:
                self.client = create_client(url, key)
                print("SupabaseStore: Client initialized successfully.")
            except Exception as e:
                print(f"SupabaseStore Warning: Failed to initialize Supabase client: {e}")
        else:
            print("SupabaseStore Warning: Missing SUPABASE_URL or SUPABASE_SERVICE_KEY. SupabaseStore will not be active.")

    def get(self, namespace: Tuple[str, ...], key: str) -> Optional[Item]:
        if not self.client:
            print("SupabaseStore Warning: client is not initialized, cannot get key.")
            return None
        
        try:
            # Match by both namespace (stored as list/array) and key
            res = self.client.table("memory_store").select("*").eq("key", key).execute()
            if res.data:
                # Filter by namespace in python to be safe with postgres array structure
                # namespace in DB is stored as e.g., ["memory", "profile"]
                for row in res.data:
                    # Supabase returns namespace as a list
                    row_namespace = tuple(row["namespace"])
                    if row_namespace == namespace:
                        return Item(
                            namespace=namespace,
                            key=key,
                            value=row["value"],
                            created_at=row.get("updated_at"),
                            updated_at=row.get("updated_at")
                        )
        except Exception as e:
            print(f"SupabaseStore Error in get({namespace}, {key}): {e}")
        return None

    def put(self, namespace: Tuple[str, ...], key: str, value: dict) -> None:
        if not self.client:
            print("SupabaseStore Warning: client is not initialized, cannot put key.")
            return
        
        try:
            data = {
                "namespace": list(namespace),
                "key": key,
                "value": value
            }
            # Upsert into memory_store table.
            # RLS needs to be disabled or configured to allow upserts.
            self.client.table("memory_store").upsert(data, on_conflict="namespace,key").execute()
            print(f"SupabaseStore: Saved key '{key}' in namespace {namespace}.")
        except Exception as e:
            print(f"SupabaseStore Error in put({namespace}, {key}): {e}")

    def delete(self, namespace: Tuple[str, ...], key: str) -> None:
        if not self.client:
            print("SupabaseStore Warning: client is not initialized, cannot delete key.")
            return
        
        try:
            self.client.table("memory_store").delete().eq("key", key).execute()
            print(f"SupabaseStore: Deleted key '{key}' in namespace {namespace}.")
        except Exception as e:
            print(f"SupabaseStore Error in delete({namespace}, {key}): {e}")

    def search(self, namespace_prefix: Tuple[str, ...], *, query: Optional[str] = None, limit: int = 10, offset: int = 0) -> list[Item]:
        # Search is not actively used in the current graph implementations, 
        # but we provide a basic structure to satisfy the BaseStore interface.
        if not self.client:
            return []
        
        try:
            res = self.client.table("memory_store").select("*").execute()
            items = []
            if res.data:
                for row in res.data:
                    ns = tuple(row["namespace"])
                    if ns[:len(namespace_prefix)] == namespace_prefix:
                        # Simple query filtering if needed
                        if query and query.lower() not in str(row["value"]).lower():
                            continue
                        items.append(
                            Item(
                                namespace=ns,
                                key=row["key"],
                                value=row["value"],
                                created_at=row.get("updated_at"),
                                updated_at=row.get("updated_at")
                            )
                        )
            # Apply limit and offset
            return items[offset:offset+limit]
        except Exception as e:
            print(f"SupabaseStore Error in search: {e}")
            return []

    def batch(self, ops: Iterable[Op]) -> list[Result]:
        results = []
        for op in ops:
            if isinstance(op, GetOp):
                results.append(self.get(op.namespace, op.key))
            elif isinstance(op, PutOp):
                self.put(op.namespace, op.key, op.value)
                results.append(None)
            elif isinstance(op, SearchOp):
                results.append(self.search(
                    op.namespace_prefix,
                    query=op.query,
                    limit=op.limit,
                    offset=op.offset
                ))
            else:
                results.append(None)
        return results

    async def abatch(self, ops: Iterable[Op]) -> list[Result]:
        return self.batch(ops)
