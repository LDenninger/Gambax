import numpy as np
import matplotlib.pyplot as plt; plt.style.use('seaborn-v0_8')
import json

from gambax.core import LLMClient
from gambax.utils import message_template



if __name__ == "__main__":
    client = LLMClient()

    x_points = np.arange(0, 20, 0.5)
    y_points = np.arange(0, 5, 5/x_points.shape[0])
    y_points += np.random.normal(scale=0.5, size=y_points.shape)

    messages = [
        message_template("system", "You are a helpful AI assistant that is given questions it should answer precisely."),
        message_template("user", f"Points: x: {x_points.tolist()}, y: {y_points.tolist()}"),
        message_template("user", f"Compute a line best fitting the given points"),
    ]

    response = client.request_response(messages)
    coeff = response
    print("Assistant response:\n", response)

    line_points = coeff[0] * x_points + coeff[1]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x_points, y_points, label="data points")
    ax.plot(x_points, line_points, label="linear regression line", c='g')
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 5)
    ax.set_title("Linear Regression")
    fig.tight_layout()
    fig.savefig("misc/linear_regression.png", bbox_inches='tight')