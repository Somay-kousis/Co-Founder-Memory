# scripts/run_midnight_loop.py
import time
from datetime import datetime
from graph.auto_graph import compiled_auto_graph

def run_smart_scheduler():
    print("⏳ Co-Founder's Memory Smart Background Daemon activated...")
    print("Monitoring system clock and historical logs for missed execution runs.\n")
    
    # Mocking state initialization. 
    # In production, you would fetch the real state dictionary containing your historic logs.
    state_buffer = {
        "chunk_memory": [],
        "temporary_memory": [],
        "retrieved_context": [],
        "extracted_memories": [],
        "final_response": "",
        "date_memory": {},  # Tracks processed days like {"2026-06-08": "Report..."}
        "auto_ready": False,
        "needs_more_search": False,
        "needs_better_words": False,
        "auto_review_count": 0
    }

    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        
        # 1. Check if today's dossier has already been created
        has_run_today = today_str in state_buffer.get("date_memory", {})
        
        # 2. TRIGGER CONDITION A: It's exactly midnight
        is_midnight = (now.hour == 0 and now.minute == 0)
        
        # 3. TRIGGER CONDITION B: Laptop was off at midnight, and we just turned it on at 8 AM
        is_missed_catchup = not has_run_today and now.hour >= 1
        
        if is_midnight or is_missed_catchup:
            if is_midnight:
                print(f"⏰ Midnight struck ({now.strftime('%H:%M:%S')}). Executing standard scheduled loop...")
            else:
                print(f"🚨 Catch-up detected at {now.strftime('%H:%M:%S')}! Laptop was offline for midnight run. Processing today's dossier now...")
            
            try:
                # Fire the graph execution thread
                updated_state = compiled_auto_graph.invoke(state_buffer)
                
                # Update our local buffer memory so it knows today is officially locked down
                if updated_state and "date_memory" in updated_state:
                    state_buffer["date_memory"] = updated_state["date_memory"]
                else:
                    # Fallback flag to prevent infinite looping if date_memory isn't returned
                    state_buffer["date_memory"][today_str] = "Completed"
                    
                print(f"🟢 Success: Dossier for {today_str} completed and state updated.")
                
            except Exception as e:
                print(f"❌ Automation graph error during execution: {e}")
            
            # Sleep for 61 seconds to cleanly pass any midnight matching window safely
            time.sleep(61)
            
        # Check every 60 seconds to keep your battery usage at zero
        time.sleep(60)

if __name__ == "__main__":
    run_smart_scheduler()