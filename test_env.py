"""Test script for Delivery Route Environment"""
import requests
import json
import time

BASE_URL = "http://localhost:7860"

def test_environment():
    """Test all endpoints of the environment"""
    
    print("🧪 Testing Delivery Route Optimization Environment")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    health_response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {health_response.json()}")
    
    # Test reset with different difficulties
    difficulties = ["easy", "medium", "hard"]
    
    for difficulty in difficulties:
        print(f"\n2. Testing reset with {difficulty} difficulty...")
        reset_data = {
            "difficulty": difficulty,
            "seed": 42
        }
        reset_response = requests.post(f"{BASE_URL}/reset", json=reset_data)
        reset_result = reset_response.json()
        session_id = reset_result["session_id"]
        
        print(f"   Session ID: {session_id}")
        print(f"   Initial observation keys: {reset_result['observation'].keys()}")
        print(f"   Total customers: {reset_result['info']['total_customers']}")
        print(f"   Vehicle capacity: {reset_result['info']['max_capacity']}")
        
        # Test a few steps
        print(f"\n3. Testing steps for {difficulty} difficulty...")
        total_reward = 0
        
        for step_num in range(10):
            # Alternate between actions
            action = step_num % 4  # Use actions 0-3
            
            step_data = {
                "session_id": session_id,
                "action": action
            }
            
            step_response = requests.post(f"{BASE_URL}/step", json=step_data)
            step_result = step_response.json()
            
            total_reward += step_result["reward"]
            
            print(f"   Step {step_num + 1}:")
            print(f"     Action: {step_result['info']['action_taken']}")
            print(f"     Reward: {step_result['reward']:.2f}")
            print(f"     Pending deliveries: {step_result['observation']['pending_deliveries']}")
            print(f"     Cumulative reward: {step_result['info']['cumulative_reward']:.2f}")
            
            if step_result["terminated"]:
                print(f"     Episode terminated!")
                break
        
        # Test state endpoint
        print(f"\n4. Testing state endpoint...")
        state_data = {"session_id": session_id}
        state_response = requests.post(f"{BASE_URL}/state", json=state_data)
        state_result = state_response.json()
        print(f"   Current time: {state_result['observation']['current_time']:.2f} minutes")
        print(f"   Traffic level: {state_result['observation']['traffic_level']:.2f}")
        
        # Test close endpoint
        print(f"\n5. Closing session...")
        close_response = requests.post(f"{BASE_URL}/close?session_id={session_id}")
        print(f"   Close result: {close_response.json()}")
        
        print(f"\n   Total reward for {difficulty}: {total_reward:.2f}")
        print("-" * 30)
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2)
    test_environment()