// https://codenebula.io/javascript/frontend/dataviz/2019/04/18/automatically-generate-chart-colors-with-chart-js-d3s-color-scales/

function calculatePoint(i, intervalSize, colorRangeInfo) {
  var { colorStart, colorEnd, useEndAsStart } = colorRangeInfo;
  return (useEndAsStart
    ? (colorEnd - (i * intervalSize))
    : (colorStart + (i * intervalSize)));
}

/* Must use an interpolated color scale, which has a range of [0, 1] */
function interpolateColors(dataLength, colorScale, colorRangeInfo) {
  var { colorStart, colorEnd } = colorRangeInfo;
  var colorRange = colorEnd - colorStart;
  var intervalSize = colorRange / dataLength;
  var i, colorPoint;
  var colorArray = [];

  for (i = 0; i < dataLength; i++) {
    colorPoint = calculatePoint(i, intervalSize, colorRangeInfo);
    colorArray.push(colorScale(colorPoint));
  }

  return colorArray;
}

// -----------------------------------------------------------

function initResearchChart() {        
  if (!KTUtil.getByID('chart_research')) {
      return;
  }
  let synCount = $('#chart_research').data('syn');
  let antCount = $('#chart_research').data('ant');
  let indCount = $('#chart_research').data('ind');
  let total = $('#chart_research').data('total');

  var config = {
      type: 'doughnut',
      data: {
          datasets: [{
              data: [
                  synCount, antCount, indCount, total - synCount - antCount - indCount
              ],
              backgroundColor: [
                  KTApp.getStateColor('success'),
                  KTApp.getStateColor('danger'),
                  KTApp.getStateColor('gray'),
                  KTApp.getStateColor('dark')
              ]
          }],
          labels: [
              'Synergistic',
              'Antagonistic',
              'Independent',
              'Single'
          ]
      },
      options: {
          cutoutPercentage: 75,
          responsive: true,
          maintainAspectRatio: false,
          legend: {
              display: false,
              position: 'top',
          },
          title: {
              display: false,
              text: 'Technology'
          },
          animation: {
              animateScale: true,
              animateRotate: true
          },
          tooltips: {
              enabled: true,
              intersect: false,
              mode: 'nearest',
              bodySpacing: 5,
              yPadding: 10,
              xPadding: 10, 
              caretPadding: 0,
              displayColors: false,
              backgroundColor: KTApp.getStateColor('brand'),
              titleFontColor: '#ffffff', 
              cornerRadius: 4,
              footerSpacing: 0,
              titleSpacing: 0
          }
      }
  };

  var ctx = KTUtil.getByID('chart_research').getContext('2d');
  var myDoughnut = new Chart(ctx, config);
}

function populateLegend(colorCode, allFactors, id = '#topFactors') {
  let html2populate = '';
  let first4Factors = $('#chart_factor').data('first4factors');
  for (const factor of first4Factors){
    html2populate += `
    <div class="kt-widget14__legend">
        <span class="kt-widget14__bullet" style="background-color: ${colorCode[factor]};"></span>
        <span class="kt-widget14__stats"><span class="animateNumber" data-value="${allFactors.get(factor)}">0</span> ${factor}</span>
    </div>`
  }
  $(id).html(html2populate)
}

function initFactorChart() {        
  if (!KTUtil.getByID('chart_factor')) {
      return;
  }

  let allFactors = new Map(Object.entries($('#chart_factor').data('factors')));
  const COLORS = interpolateColors(Array.from(allFactors.keys()).length, d3.interpolateTurbo, {colorStart: 0, colorEnd: 1, useEndAsStart: true});
  const FACTOR_DATA = Array.from(allFactors.values());
  const FACTOR_LABELS = Array.from(allFactors.keys());
  var colorCodedLabels = {};

  for (let index = 0; index < COLORS.length; index++) {
    colorCodedLabels[FACTOR_LABELS[index]] = COLORS[index];    
  }
  populateLegend(colorCodedLabels, allFactors);

  var config = {
      type: 'doughnut',
      data: {
          datasets: [{
              data: FACTOR_DATA,
              backgroundColor: COLORS,
          }],
          labels: FACTOR_LABELS
      },
      options: {
          cutoutPercentage: 75,
          responsive: true,
          maintainAspectRatio: false,
          legend: {
              display: false,
              position: 'right',
          },
          title: {
              display: false,
              text: 'Technology'
          },
          animation: {
              animateScale: true,
              animateRotate: true
          },
          tooltips: {
              enabled: true,
              intersect: false,
              mode: 'nearest',
              bodySpacing: 5,
              yPadding: 10,
              xPadding: 10, 
              caretPadding: 0,
              displayColors: false,
              backgroundColor: KTApp.getStateColor('brand'),
              titleFontColor: '#ffffff', 
              cornerRadius: 4,
              footerSpacing: 0,
              titleSpacing: 0
          }
      }
  };

  var ctx = KTUtil.getByID('chart_factor').getContext('2d');
  var myDoughnut = new Chart(ctx, config);
}

function initTargetChart() {        
  if (!KTUtil.getByID('chart_target')) {
      return;
  }

  let countSpecies = new Map(Object.entries($('#chart_target').data('species')));

  var config = {
      type: 'doughnut',
      data: {
          datasets: [{
              data: Array.from(countSpecies.values()),
              backgroundColor: [
                KTApp.getStateColor('primary'),
                KTApp.getStateColor('danger'),
                KTApp.getStateColor('warning'),
                  KTApp.getStateColor('dark'),
              ]
          }],
          labels: Array.from(countSpecies.keys())
      },
      options: {
          cutoutPercentage: 75,
          responsive: true,
          maintainAspectRatio: false,
          legend: {
              display: false,
              position: 'top',
          },
          title: {
              display: false,
              text: 'Technology'
          },
          animation: {
              animateScale: true,
              animateRotate: true
          },
          tooltips: {
              enabled: true,
              intersect: false,
              mode: 'nearest',
              bodySpacing: 5,
              yPadding: 10,
              xPadding: 10, 
              caretPadding: 0,
              displayColors: false,
              backgroundColor: KTApp.getStateColor('brand'),
              titleFontColor: '#ffffff', 
              cornerRadius: 4,
              footerSpacing: 0,
              titleSpacing: 0
          }
      }
  };

  var ctx = KTUtil.getByID('chart_target').getContext('2d');
  var myDoughnut = new Chart(ctx, config);
}

$(document).ready(function() {

      initResearchChart();
      initFactorChart();
      initTargetChart();

      $('.animateNumber').each(function() {
        $(this).animateNumber(
          {
            number:$(this).data('value'),
            // optional custom step function
            // using here to keep '%' sign after number
            numberStep: function(now, tween) {
              var floored_number = Math.floor(now),
                  target = $(tween.elem);
        
              target.text(floored_number);
            }
          },
          {
            easing: 'swing',
            duration: 1000
          }
        )});
});