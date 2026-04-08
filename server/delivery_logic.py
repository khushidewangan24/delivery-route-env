def step(self, action: int) -> Tuple[float, bool, Dict[str, Any]]:
    """
    Execute one step in the environment.
    
    Returns:
        reward: float - Reward for this step
        done: bool - Whether episode is complete
        info: dict - Additional information
    """
    info = {"action": self.actions.get(action, "unknown")}
    done = False
    reward = 0.0
    
    if action == 0:  # next_stop
        if self.remaining_stops:
            # Get next stop
            next_stop = self.remaining_stops[0]
            
            # Calculate distance and travel time
            distance = self._calculate_distance(
                self.current_location,
                [next_stop.lat, next_stop.lon]
            )
            travel_time = self._calculate_travel_time(distance)
            
            # Update time and location
            self.current_time += travel_time
            self.current_location = [next_stop.lat, next_stop.lon]
            
            # Check if delivery is successful
            delivery_success = True
            reward_components = {}
            
            # Check time window
            if self.current_time < next_stop.time_window_start:
                # Early arrival - must wait
                wait_time = next_stop.time_window_start - self.current_time
                self.current_time += wait_time
                reward_components["early_arrival_penalty"] = -2.0
                reward -= 2.0
            elif self.current_time > next_stop.time_window_end:
                # Late arrival - partial penalty
                lateness = self.current_time - next_stop.time_window_end
                penalty = min(10.0, lateness * 0.5)
                reward_components["late_penalty"] = -penalty
                reward -= penalty
                delivery_success = lateness < 30  # Too late = failed delivery
            
            # Check capacity
            if self.vehicle_capacity < next_stop.weight:
                delivery_success = False
                reward_components["capacity_exceeded"] = -5.0
                reward -= 5.0
                info["error"] = "Capacity exceeded"
            
            if delivery_success:
                # Successful delivery
                self.vehicle_capacity -= next_stop.weight
                self.completed_deliveries.append(next_stop.id)
                self.remaining_stops.pop(0)
                
                # Base reward for delivery
                base_reward = 10.0
                
                # Priority bonus
                priority_bonus = next_stop.priority * 1.0
                
                # Time window bonus
                time_window_center = (next_stop.time_window_start + next_stop.time_window_end) / 2
                time_accuracy = max(0, 1 - abs(self.current_time - time_window_center) / 30)
                time_bonus = time_accuracy * 5.0
                
                reward += base_reward + priority_bonus + time_bonus
                
                reward_components.update({
                    "base_delivery": base_reward,
                    "priority_bonus": priority_bonus,
                    "time_bonus": time_bonus
                })
                
                info["delivery_success"] = True
                info["customer_id"] = next_stop.id
            else:
                info["delivery_success"] = False
            
            # Update traffic randomly
            self.traffic_level = min(1.0, max(0.1, 
                self.traffic_level + random.uniform(-0.2, 0.2)))
            
            info["reward_breakdown"] = reward_components
            info["travel_distance"] = distance
            info["travel_time"] = travel_time
            
            # Check if all deliveries complete
            if not self.remaining_stops:
                done = True
                # Completion bonus
                completion_bonus = 50.0
                reward += completion_bonus
                info["completion_bonus"] = completion_bonus
                
        else:
            # No stops remaining
            done = True
            reward += 0
            info["message"] = "No stops remaining"
    
    elif action == 1:  # wait_5min
        self.current_time += 5
        # Traffic might improve while waiting
        self.traffic_level = max(0.1, self.traffic_level - random.uniform(0, 0.1))
        reward -= 2.0  # Penalty for waiting
        info["traffic_level"] = self.traffic_level
    
    elif action == 2:  # recalculate
        # Sort remaining stops by optimal route
        if self.remaining_stops:
            # Simple TSP heuristic - sort by distance from current location
            self.remaining_stops.sort(key=lambda x: 
                self._calculate_distance(self.current_location, [x.lat, x.lon]))
        reward -= 1.0  # Small cost for recalculation
        info["route_recalculated"] = True
    
    elif action == 3:  # skip_current
        if self.remaining_stops:
            skipped = self.remaining_stops.pop(0)
            self.remaining_stops.append(skipped)  # Move to end
            penalty = -5.0 * (1 + skipped.priority * 0.1)
            reward += penalty
            info["skipped_customer"] = skipped.id
            info["penalty"] = penalty
    
    elif action == 4:  # priority_delivery
        if self.remaining_stops:
            # Sort by priority (highest first)
            self.remaining_stops.sort(key=lambda x: x.priority, reverse=True)
        reward -= 0.5
        info["priority_sorted"] = True
    
    elif action == 5:  # capacity_check
        # Optimize load based on capacity
        if self.remaining_stops:
            total_weight = sum(s.weight for s in self.remaining_stops)
            info["total_remaining_weight"] = total_weight
            info["capacity_utilization"] = 1 - (self.vehicle_capacity / self.config["max_capacity"])
        reward -= 0.5
    
    elif action == 6:  # time_window_check
        # Check time window compliance
        if self.remaining_stops:
            urgent_stops = [s for s in self.remaining_stops 
                          if s.time_window_end - self.current_time < 30]
            info["urgent_stops"] = len(urgent_stops)
            if urgent_stops:
                # Move urgent stops to front
                for stop in reversed(urgent_stops):
                    self.remaining_stops.remove(stop)
                    self.remaining_stops.insert(0, stop)
        reward -= 0.5
    
    elif action == 7:  # emergency_return
        # Return to warehouse
        warehouse_location = [40.7128, -74.0060]
        distance = self._calculate_distance(self.current_location, warehouse_location)
        travel_time = self._calculate_travel_time(distance)
        self.current_time += travel_time
        self.current_location = warehouse_location
        
        # Penalty for unfinished deliveries
        penalty = -10.0 * len(self.remaining_stops)
        reward += penalty
        info["unfinished_deliveries"] = len(self.remaining_stops)
        info["emergency_return_penalty"] = penalty
        done = True
    
    # Check max steps
    if self.step_count >= self.max_steps:
        done = True
        info["max_steps_reached"] = True
    
    return reward, done, info