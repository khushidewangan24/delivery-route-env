import os
import sys
from openai import OpenAI
from environment import DeliveryRouterEnv
from models import Action
from tasks.easy import easy_config
from tasks.medium import medium_config
from tasks.hard import hard_config
from graders.easy_grader import grade as grade_easy
from graders.medium_grader import grade as grade_medium
from graders.hard_grader import grade as grade_hard

# Initialize OpenAI client (required)
client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.environ.get("HF_TOKEN", "")
)
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

def create_agent_policy(env_instance):
    """Returns a function that maps observation to action using LLM"""
    def policy(obs):
        prompt = f"""You are a delivery route optimizer. Current status:
- Position: {obs.current_position}
- Time: {obs.current_time} min
- Deliveries left: {obs.remaining_count}
- Nearest delivery distance: {obs.nearest_delivery_distance:.1f}
- Traffic ahead: {obs.traffic_ahead}
- Fuel: {obs.fuel_percent:.1f}%
- On-time rate: {obs.on_time_rate:.2f}

Choose next delivery ID (0-{env_instance.config.num_deliveries-1} that's still remaining),
whether to reroute (True/False), and speed multiplier (0.5-1.5).

Respond with: delivery_id, reroute, speed_multiplier
Example: 3, True, 1.2"""
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=50
        )
        
        # Parse response (simple parsing for demo)
        try:
            parts = response.choices[0].message.content.strip().split(',')
            delivery_id = int(parts[0].strip())
            reroute = parts[1].strip().lower() == 'true'
            speed_mult = float(parts[2].strip())
            speed_mult = max(0.5, min(1.5, speed_mult))
        except:
            # Fallback action
            delivery_id = env_instance.state.remaining_deliveries[0] if env_instance.state.remaining_deliveries else 0
            reroute = False
            speed_mult = 1.0
        
        return Action(next_delivery_id=delivery_id, reroute=reroute, speed_multiplier=speed_mult)
    
    return policy

def run_evaluation():
    """Main inference with strict logging format"""
    print("[START] task=delivery_router")
    
    # Easy task
    env_easy = DeliveryRouterEnv(easy_config)
    agent_easy = create_agent_policy(env_easy)
    score_easy = grade_easy(agent_easy, env_easy)
    print(f"[STEP] task=easy score={score_easy:.4f}")
    
    # Medium task
    env_medium = DeliveryRouterEnv(medium_config)
    agent_medium = create_agent_policy(env_medium)
    score_medium = grade_medium(agent_medium, env_medium)
    print(f"[STEP] task=medium score={score_medium:.4f}")
    
    # Hard task
    env_hard = DeliveryRouterEnv(hard_config)
    agent_hard = create_agent_policy(env_hard)
    score_hard = grade_hard(agent_hard, env_hard)
    print(f"[STEP] task=hard score={score_hard:.4f}")
    
    # Final summary
    final_scores = [score_easy, score_medium, score_hard]
    print(f"[END] final_scores={final_scores}")
    return final_scores

if __name__ == "__main__":
    run_evaluation()