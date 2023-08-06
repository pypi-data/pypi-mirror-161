def update_lr(optimizer, schedule, step):
    for param_group in optimizer.param_groups:
        param_group['lr'] = schedule[step]


def get_lr(optimizer):
    for param_group in optimizer.param_groups:
        return param_group['lr']

def poly_scheduler(initial_value, final_value, epochs, niter_per_epoch=1, gamma=0.9):
    niter = epochs * niter_per_epoch
    schedule = []
    for i in range(niter):
        item = initial_value * ((1.0 - i / niter) ** gamma)
        schedule.append(item if item > final_value else final_value)

    return schedule