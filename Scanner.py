<html>

<head>
  <title>Option Chain Analysis</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css"
    crossorigin="anonymous" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/handlebars.js/4.1.2/handlebars.min.js"></script>
</head>

<body onload="init()">
  <div class="container-fluid">
    <h1>Option Chain</h1>
    <form class="inline-form">
      <fieldset>
        <div class="form-group-inline">
          <label for="expiryDate" class="form-label">Expiry Date</label>
          <select onchange="generateTbl()" name="expiryDate" id="expiryDate"></select>
          &nbsp;&nbsp;<span id="lastUpdated"></span>
        </div>
      </fieldset>
    </form>
    <div id="content">Loading...</div>
  </div>

  <script id="chain" type="text/x-handlebars-template">
    <table class="table table-bordered table-striped">
      <thead>
        <tr>
          <th>Interpretation</th>
          <th>Call Volume</th>
          <th>Call Net OI</th>
          <th>Call change in OI</th>
          <th>Call Price change</th>
          <th>Call LTP</th>
          <th>strike</th>
          <th>Put LTP</th>
          <th>Put Price Change</th>
          <th>Put Change in OI</th>
          <th>Put Net OI</th>
          <th>Put Volume</th>
          <th>Interpretation</th>
          <!-- <th>PCR</th>
          <th>PCR Indication</th> -->
        </tr>
      </thead>
      <tbody>
        {{#each option_chain}}
        <tr>
          {{#if CE_A.trend }}
            <td class="text-success bg-success"><i class="glyphicon glyphicon-arrow-up"></i> {{ CE_A.i }} </td>
          {{else}}
            <td class="text-danger bg-danger"><i class="glyphicon glyphicon-arrow-down"></i> {{ CE_A.i }}</td>
          {{/if}}
          <td class="text-right">{{ CE.totalTradedVolume }}</td>
          <td class="text-right">{{ CE.openInterest }}</td>
          {{#if CE_A.OI}}
            <td class="text-right text-success bg-success">{{ CE.changeinOpenInterest }} <i class="glyphicon glyphicon-arrow-up"></i></td>
          {{else }}
            <td class="text-right text-danger bg-danger">{{ CE.changeinOpenInterest }} <i class="glyphicon glyphicon-arrow-down"></i></td>
          {{/if}}
          {{#if CE_A.price}}
            <td class="text-right text-success bg-success">{{ CE.change }} <i class="glyphicon glyphicon-arrow-up"></i></td>
          {{else}}
            <td class="text-right text-danger bg-danger">{{ CE.change }} <i class="glyphicon glyphicon-arrow-down"></i></td>
          {{/if}}
          <td class="text-right">{{ CE.lastPrice }}</td>
          <th class="text-center">{{ strikePrice }}</th>
          <td class="text-right">{{ PE.lastPrice }}</td>

          {{#if PE_A.price}}
            <td class="text-right text-success bg-success">{{ PE.change }} <i class="glyphicon glyphicon-arrow-up"></i></td>
          {{else}}
            <td class="text-right text-danger bg-danger">{{ PE.change }} <i class="glyphicon glyphicon-arrow-down"></i></td>
          {{/if}}

          {{#if PE_A.OI}}
            <td class="text-right text-success bg-success">{{ PE.changeinOpenInterest }} <i class="glyphicon glyphicon-arrow-up"></i></td>
          {{else }}
            <td class="text-right text-danger bg-danger">{{ PE.changeinOpenInterest }} <i class="glyphicon glyphicon-arrow-down"></i></td>
          {{/if}}

          <td class="text-right">{{ PE.openInterest }}</td>
          <td class="text-right">{{ PE.totalTradedVolume }}</td>
          {{#if PE_A.trend }}
            <td class="text-success bg-success"><i class="glyphicon glyphicon-arrow-up"></i> {{ PE_A.i }}</td>
          {{else}}
            <td class="text-danger bg-danger"><i class="glyphicon glyphicon-arrow-down"></i> {{ PE_A.i }}</td>
          {{/if}}
          <!-- <td>PCR</td>
          <td>PCR Indication</td> -->
        </tr>
        {{/each}}
      </tbody>
    </table>

    <p>Developed by <a href="https://www.facebook.com/aaditya.tamrakar.9" target="_blank">Aaditya Tamrakar</a></p>
  </script>

  <script>
    var optionChainData, lastUpdated, underlyingValue, selected_expiry, option_chain = [];

    function getData(cb) {
      return new Promise((resolve, reject) => {
        if (optionChainData != null) {
          resolve(optionChainData);
        } else {
          fetch('/chain')
            .then(resp => {
              if (resp.status != 200) throw new Error('something went wrong');
              return resp.json();
            })
            .then(data => {
              optionChainData = data;
              lastUpdated = data.records.timestamp;
              document.querySelector('#lastUpdated').innerHTML = 'Last Updated: ' + lastUpdated;
              resolve(optionChainData);
            })
            .catch(err => {
              document.getElementById('content').innerHTML = "Error Occured: " + err.toString();
              reject('error');
            })
        }
      });
    }

    function init() {
      getData().then(function (data) {
        expiryDates = data.records.expiryDates;
        underlyingValue = data.records.underlyingValue;
        selected_expiry = data.records.expiryDates[0];
        fillExpiryDate(expiryDates);
        // generateTbl(data);
        document.querySelector('#expiryDate').value = selected_expiry;
        generateTbl();
      })
    }

    function generateTbl() {
      let expiryDate = document.querySelector('#expiryDate').value;
      let option_chain = optionChainData.records.data.filter(c => {
        return (
            c.strikePrice <= 800 + (parseInt(underlyingValue / 100) * 100)) &&
          (c.strikePrice >= (parseInt(underlyingValue / 100) * 100) - 800) &&
          c.expiryDate == expiryDate
      });

      option_chain = JSON.parse(JSON.stringify(option_chain)).map(optionChainAnalysis);

      let context = {
        option_chain,
        lastUpdated,
        underlyingValue,
        selected_expiry
      };
      renderTbl(context);
    }

    function fillExpiryDate(expiryDates) {
      let expirySelect = document.querySelector('#expiryDate');
      expirySelect.innerHTML = expiryDates.map((c, idx) => {
        return `<option value="${c}">${c}</option>`;
      });
    }

    function optionChainAnalysis(strike) {
      strike.CE.change = strike.CE.change ? strike.CE.change.toFixed(1) : '';
      strike.PE.change = strike.PE.change ? strike.PE.change.toFixed(1) : '';

      strike.PE.openInterest = String(strike.PE.openInterest).replace(/(\d)(?=(\d\d)+\d$)/g, "$1,");
      strike.CE.openInterest = String(strike.CE.openInterest).replace(/(\d)(?=(\d\d)+\d$)/g, "$1,");
      strike.PE.totalTradedVolume = String(strike.PE.totalTradedVolume).replace(/(\d)(?=(\d\d)+\d$)/g,
        "$1,");
      strike.CE.totalTradedVolume = String(strike.CE.totalTradedVolume).replace(/(\d)(?=(\d\d)+\d$)/g,
        "$1,");

      strike.CE_A = {};
      strike.PE_A = {};

      strike.CE_A.price = strike.CE.change > 0 ? 1 : 0;
      strike.CE_A.OI = strike.CE.changeinOpenInterest > 0 ? 1 : 0;

      strike.PE_A.price = strike.PE.change > 0 ? 1 : 0;
      strike.PE_A.OI = strike.PE.changeinOpenInterest > 0 ? 1 : 0;

      if (strike.CE_A.price === 0 && strike.CE_A.OI === 0) strike.CE_A.i = 'Long Liquidation';
      else if (strike.CE_A.price === 0 && strike.CE_A.OI === 1) strike.CE_A.i = 'Short Buildup';
      else if (strike.CE_A.price === 1 && strike.CE_A.OI === 1) strike.CE_A.i = 'Short Covering';
      else if (strike.CE_A.price === 1 && strike.CE_A.OI === 0) strike.CE_A.i = 'Long Buildup';

      if (strike.PE_A.price === 0 && strike.PE_A.OI === 0) strike.PE_A.i = 'Long Liquidation';
      else if (strike.PE_A.price === 0 && strike.PE_A.OI === 1) strike.PE_A.i = 'Short Buildup';
      else if (strike.PE_A.price === 1 && strike.PE_A.OI === 1) strike.PE_A.i = 'Short Covering';
      else if (strike.PE_A.price === 1 && strike.PE_A.OI === 0) strike.PE_A.i = 'Long Buildup';

      strike.PE_A.trend = (strike.PE_A.i == 'Long Liquidation' || strike.PE_A.i == 'Short Buildup') ?
        0 : 1;
      strike.CE_A.trend = (strike.CE_A.i == 'Long Liquidation' || strike.CE_A.i == 'Short Buildup') ?
        1 : 0;

      return strike;
    }

    function renderTbl(context) {
      var source = document.getElementById("chain").innerHTML;
      var template = Handlebars.compile(source);
      document.getElementById('content').innerHTML = template(context);
    }

  </script>
</body>

</html>