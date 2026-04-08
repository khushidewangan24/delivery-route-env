"""FastAPI server for Delivery Route Optimization Environment"""
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .models import (
    ResetRequest, StepRequest, StateRequest,
    EnvironmentResponse, HealthResponse
)
from .delivery_logic import DeliveryEnvironment
from .logger import logger


# Initialize FastAPI app
app = FastAPI(
    title="Delivery Route Optimization Environment",
    description="OpenEnv-compliant environment for delivery route optimization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active environments
active_environments: Dict[str, DeliveryEnvironment] = {}


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Delivery Route Optimization Environment",
        "status": "running",
        "active_sessions": len(active_environments),
        "endpoints": ["/reset", "/step", "/state", "/health", "/close"]
    }


@app.get("/health", tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint for Docker and monitoring"""
    logger.info("Health check called", extra={"active_sessions": len(active_environments)})
    return HealthResponse(
        status="healthy",
        active_sessions=len(active_environments)
    )


@app.post("/reset", response_model=EnvironmentResponse, tags=["Environment"])
async def reset(request: ResetRequest) -> EnvironmentResponse:
    """
    Reset the environment to initial state.
    
    Creates a new session or resets an existing one.
    Returns initial observation.
    """
    session_id = request.session_id or str(uuid.uuid4())
    difficulty = request.difficulty or "medium"
    seed = request.seed
    
    logger.info(
        f"Reset called",
        extra={
            "session_id": session_id,
            "difficulty": difficulty,
            "seed": seed
        }
    )
    
    try:
        # Create new environment instance
        env = DeliveryEnvironment(difficulty=difficulty, seed=seed)
        active_environments[session_id] = env
        
        # Get initial observation
        observation = env._get_observation()
        
        logger.info(
            f"Environment reset successful",
            extra={
                "session_id": session_id,
                "num_customers": len(env.remaining_stops),
                "vehicle_capacity": env.vehicle_capacity
            }
        )
        
        return EnvironmentResponse(
            session_id=session_id,
            observation=observation,
            reward=0.0,
            terminated=False,
            truncated=False,
            info={
                "difficulty": difficulty,
                "total_customers": len(env.remaining_stops),
                "max_capacity": env.vehicle_capacity,
                "max_steps": env.max_steps
            }
        )
        
    except Exception as e:
        logger.error(
            f"Error in reset",
            extra={"session_id": session_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step", response_model=EnvironmentResponse, tags=["Environment"])
async def step(request: StepRequest) -> EnvironmentResponse:
    """
    Execute one step in the environment.
    
    Takes an action and returns next observation, reward, and termination status.
    """
    session_id = request.session_id
    action = request.action
    
    # Enhanced logging for step
    logger.info(
        f"Step called",
        extra={
            "session_id": session_id,
            "action": action,
            "action_name": DeliveryEnvironment.actions.get(action, "unknown")
        }
    )
    
    # Check if session exists
    if session_id not in active_environments:
        logger.error(
            f"Session not found",
            extra={"session_id": session_id}
        )
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    env = active_environments[session_id]
    
    try:
        # Validate action
        if action not in env.actions:
            raise ValueError(f"Invalid action: {action}. Must be 0-7")
        
        # Execute action and get reward
        reward, done, info = env.step(action)
        
        # Update cumulative reward
        env.cumulative_reward += reward
        env.step_count += 1
        
        # Check if truncated (max steps reached)
        truncated = env.step_count >= env.max_steps
        terminated = done or truncated
        
        # Get observation
        observation = env._get_observation()
        
        # Enhanced logging with reward information
        logger.info(
            f"Step completed",
            extra={
                "session_id": session_id,
                "action": action,
                "reward": reward,
                "cumulative_reward": env.cumulative_reward,
                "step_number": env.step_count,
                "pending_deliveries": len(env.remaining_stops),
                "terminated": terminated,
                "truncated": truncated
            }
        )
        
        return EnvironmentResponse(
            session_id=session_id,
            observation=observation,
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            info={
                **info,
                "step_count": env.step_count,
                "cumulative_reward": env.cumulative_reward,
                "action_taken": env.actions[action],
                "completed_deliveries": len(env.completed_deliveries),
                "remaining_capacity": env.vehicle_capacity
            }
        )
        
    except Exception as e:
        logger.error(
            f"Error in step",
            extra={
                "session_id": session_id,
                "action": action,
                "error": str(e)
            },
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/state", response_model=EnvironmentResponse, tags=["Environment"])
async def state(request: StateRequest) -> EnvironmentResponse:
    """
    Get current state without taking an action.
    
    Returns current observation and metadata.
    """
    session_id = request.session_id
    
    logger.info(
        f"State called",
        extra={"session_id": session_id}
    )
    
    # Check if session exists
    if session_id not in active_environments:
        logger.error(
            f"Session not found",
            extra={"session_id": session_id}
        )
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    env = active_environments[session_id]
    
    try:
        observation = env._get_observation()
        
        logger.info(
            f"State retrieved",
            extra={
                "session_id": session_id,
                "step_count": env.step_count,
                "cumulative_reward": env.cumulative_reward
            }
        )
        
        return EnvironmentResponse(
            session_id=session_id,
            observation=observation,
            reward=0.0,
            terminated=False,
            truncated=False,
            info={
                "step_count": env.step_count,
                "cumulative_reward": env.cumulative_reward,
                "pending_deliveries": len(env.remaining_stops)
            }
        )
        
    except Exception as e:
        logger.error(
            f"Error in state",
            extra={"session_id": session_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/close", tags=["Environment"])
async def close(session_id: str):
    """
    Close and cleanup an environment session.
    """
    logger.info(
        f"Close called",
        extra={"session_id": session_id}
    )
    
    if session_id in active_environments:
        env = active_environments.pop(session_id)
        
        logger.info(
            f"Session closed",
            extra={
                "session_id": session_id,
                "final_reward": env.cumulative_reward,
                "steps_taken": env.step_count,
                "completed_deliveries": len(env.completed_deliveries)
            }
        )
        
        return {
            "status": "closed",
            "session_id": session_id,
            "final_reward": env.cumulative_reward,
            "steps_taken": env.step_count
        }
    
    return {"status": "not_found", "session_id": session_id}


@app.get("/sessions", tags=["Admin"])
async def list_sessions():
    """List all active sessions (for debugging)"""
    return {
        "active_sessions": len(active_environments),
        "sessions": [
            {
                "session_id": sid,
                "step_count": env.step_count,
                "cumulative_reward": env.cumulative_reward,
                "pending_deliveries": len(env.remaining_stops)
            }
            for sid, env in active_environments.items()
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=7860,
        reload=True,
        log_level="info"
    )