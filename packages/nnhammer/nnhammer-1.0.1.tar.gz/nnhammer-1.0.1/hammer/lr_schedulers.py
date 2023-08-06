def poly_scheduler(initial_value, final_value, epochs, niter_per_epoch=1, gamma=0.9):
    niter = epochs * niter_per_epoch
    schedule = []
    for i in range(niter):
        item = initial_value * ((1.0 - i / niter) ** gamma)
        schedule.append(item if item > final_value else final_value)

    return schedule
