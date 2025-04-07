def P_controller(error, K_p):
    theta = min(max(K_p *error,0),1)
    return theta

def PI_controller(error,last_error, K_p, K_i, integral_error, anti_windup = True):
    integral = (last_error + error)/2
    integral_error += integral
    output = K_p*error + K_i*integral_error
    if anti_windup:
        if output > 1:#or output < 0:
            integral_error = integral_error - integral
    theta = min(max(output,0),1)
    return theta, integral_error

def PID_controller(error, last_error, K_p, K_i, K_d, integral_error):
    integral = (last_error + error)/2
    integral_error += integral
    
    derivative = error-last_error

    output = K_p*error + K_i* integral_error + K_d * derivative
    theta =  min(max(output,0),1)
    return theta, integral_error