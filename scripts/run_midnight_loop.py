# scripts/run_midnight_loop.py
import time
from datetime import datetime
from graph.auto_graph import compiled_auto_graph
from storage_utils import load_state, save_state  # <-- NEW IMPORT

def run_smart_scheduler():
    print("⏳ Co-Founder's Memory Smart Background Daemon activated...")
    print("Monitoring system clock and historical logs for missed execution runs.\n")

    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        
        # Load the live state from disk right now so we have the latest data
        current_state = load_state()
        
        # 1. Check if today's dossier has already been created
        has_run_today = today_str in current_state.get("date_memory", {})
        
        # 2. TRIGGER CONDITION A: It's exactly midnight
        is_midnight = (now.hour == 0 and now.minute == 0)
        
        # 3. TRIGGER CONDITION B: Laptop was off at midnight, and we just turned it on
        is_missed_catchup = not has_run_today and now.hour >= 1
        
        if is_midnight or is_missed_catchup:
            if is_midnight:
                print(f"⏰ Midnight struck ({now.strftime('%H:%M:%S')}). Executing standard scheduled loop...")
            else:
                print(f"🚨 Catch-up detected at {now.strftime('%H:%M:%S')}! Processing today's dossier now...")
            
            try:
                # Fire the graph execution thread with real data
                updated_state = compiled_auto_graph.invoke(current_state)
                
                if updated_state:
                    # Make sure the date memory is officially logged
                    if "date_memory" not in updated_state:
                        updated_state["date_memory"] = {}
                    updated_state["date_memory"][today_str] = "Completed"
                    
                    # Persist the updated, processed state back to disk
                    save_state(updated_state)
                    
                print(f"🟢 Success: Dossier for {today_str} completed and state updated.")
                
            except Exception as e:
                print(f"❌ Automation graph error during execution: {e}")
            
            # Sleep for 61 seconds to cleanly pass any midnight matching window safely
            time.sleep(61)
            
        # Check every 60 seconds to keep your battery usage at zero
        time.sleep(60)

if __name__ == "__main__":
    run_smart_scheduler()