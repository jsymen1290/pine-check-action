# Pine Check GitHub Action

Checks the TradingView Pine Script files in your repository on every push or pull request and annotates the lines where a backtest will not match live trading: future data (`lookahead_on` without an offset), unconfirmed higher-timeframe values, signals drawn on past bars, realtime-only state, fill and cost assumptions, alerts on unconfirmed bars.

```yaml
name: pine-check
on: [push, pull_request]
jobs:
  pine:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jsymen1290/pine-check-action@v1
        with:
          files: "**/*.pine"      # default
          mode: integrity          # or lint
          fail-on: error           # error | warning | never
          api-key: ${{ secrets.PINE_CHECK_API_KEY }}   # optional
```

Without a key the free trial applies (30 checks a day). Plans: [pine.pokt-agent.com](https://pine.pokt-agent.com/).
Static checks only: they do not compile or run the script, and a clean result says nothing about profitability.

## Example output

```
::error file=strategies/breakout.pine,line=3,title=P201::request.security(..., lookahead_on) without a [1]-style offset reads the future on historical bars
strategies/breakout.pine: FAIL {"error": 1, "warning": 1, "info": 0}
```

Rules: [pine.pokt-agent.com/v1/rules](https://pine.pokt-agent.com/v1/rules) · Service: [pine.pokt-agent.com](https://pine.pokt-agent.com/)
