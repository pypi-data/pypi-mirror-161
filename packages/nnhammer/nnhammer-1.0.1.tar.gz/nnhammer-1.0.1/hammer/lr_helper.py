def update_lr(optimizer, schedule, step):
    for param_group in optimizer.param_groups:
        param_group['lr'] = schedule[step]


def get_lr(optimizer):
    for param_group in optimizer.param_groups:
        return param_group['lr']
