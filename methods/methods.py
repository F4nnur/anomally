from sklearn.ensemble import IsolationForest


def check_anomaly(df, metric, a=4, n=5):
    df['q25'] = df[metric].shift(1).rolling(n).quantile(0.25)
    df['q75'] = df[metric].shift(1).rolling(n).quantile(0.75)
    df['igr'] = df['q75'] - df['q25']
    df['up'] = df['q75'] - a * df['igr']
    df['low'] = df['q25'] - a * df['igr']

    df['up'] = df['up'].rolling(n, center=True, min_periods=1).mean()
    df['low'] = df['up'].rolling(n, center=True, min_periods=1).mean()

    if df[metric].iloc[-1] < df['low'].iloc[-1] or df[metric].iloc[-1] > df['up'].iloc[-1]:
        is_alert = 1
    else:
        is_alert = 0
    return is_alert, df


def check_anomaly_std(df, metric, threshold=3):
    mean = df[metric].mean()
    std = df[metric].std()
    upper_bound = mean + threshold * std
    lower_bound = mean - threshold * std

    if df[metric].iloc[-1] > upper_bound or df[metric].iloc[-1] < lower_bound:
        is_alert = 1
    else:
        is_alert = 0

    return is_alert


def check_anomaly_isolation_forest(df, metric, contamination=0.05):
    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(df[[metric]])

    if model.predict([[df[metric].iloc[-1]]])[0] == -1:
        is_alert = 1
    else:
        is_alert = 0

    return is_alert
