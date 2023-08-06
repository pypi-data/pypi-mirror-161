import torch.nn.functional as f
import torch


def RATIO(y, y_hat):
    """
    RATIO loss implementation, this loss is implemented with the MSE loss, but it can be changed to any other loss function
    :param y: real TTE
    :param y_hat: predicted TTE
    :return: RATIO loss
    """
    # censored = 0
    # uncensored = 1
    loss = 0.
    uncensored_idx = y[:, 0] == 1
    censored_idx = y[:, 0] == 0

    y_hat = y_hat.flatten()
    if any(uncensored_idx):
        loss += f.mse_loss(y[uncensored_idx, 1], y_hat[uncensored_idx]) + f.l1_loss(y[uncensored_idx, 1],
                                                                                    y_hat[uncensored_idx]) * 0.001

    y_cen, y_hat_cen = y[censored_idx], y_hat[censored_idx]
    if len(y_cen) == 0:
        if type(loss) == float:
            loss = torch.tensor(0., torch.float32, requires_grad=True)
        return loss

    to_change = y_hat_cen.flatten() < y_cen[:, 1].flatten()
    if any(to_change):
        loss += f.mse_loss(y_cen[to_change, 1], y_hat_cen[to_change]) * 0.5

    not_changed = len(y_cen) - sum(to_change)

    if (len(y_hat) - not_changed) != 0:
        loss = (loss * len(y_hat)) / (len(y_hat) - not_changed)
    else:
        loss = torch.tensor(loss, dtype=torch.float32, requires_grad=True)
    return loss
