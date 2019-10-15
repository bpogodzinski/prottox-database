function initResearchChart() {        
  if (!KTUtil.getByID('chart_research')) {
      return;
  }

  var randomScalingFactor = function() {
      return Math.round(Math.random() * 100);
  };

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

function initFactorChart() {        
  if (!KTUtil.getByID('chart_factor')) {
      return;
  }

  var randomScalingFactor = function() {
      return Math.round(Math.random() * 100);
  };

  var config = {
      type: 'doughnut',
      data: {
          datasets: [{
              data: [
                  countNotToxin, countChimeric, countFactors - countNotToxin - countChimeric
              ],
              backgroundColor: [
                  KTApp.getStateColor('warning'),
                  KTApp.getStateColor('danger'),
                  KTApp.getStateColor('primary'),
              ]
          }],
          labels: [
              'Non-standard',
              'Chimeric',
              'Standard',
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

  var ctx = KTUtil.getByID('chart_factor').getContext('2d');
  var myDoughnut = new Chart(ctx, config);
}

function initTargetChart() {        
  if (!KTUtil.getByID('chart_target')) {
      return;
  }

  var randomScalingFactor = function() {
      return Math.round(Math.random() * 100);
  };

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
//TODO: Add animate numbers to target
$(document).ready(function() {
    $('#syn-count').animateNumber(
        {
          number: synCount,
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
      );
    $('#ant-count').animateNumber(
        {
          number: antCount,
      
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
      );
    $('#ind-count').animateNumber(
        {
          number: indCount,
      
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
      );
    $('#single-count').animateNumber(
        {
          number: total - synCount - antCount - indCount,
      
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
      );
    $('#total-count').animateNumber(
        {
          number: total,
      
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
      );
    $('#factor-count').animateNumber(
        {
          number: countFactors,
      
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
      );
    $('#standard-count').animateNumber(
        {
          number: countFactors - countChimeric - countNotToxin,
      
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
      );
    $('#chimeric-count').animateNumber(
        {
          number: countChimeric,
      
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
      );
    $('#nontoxin-count').animateNumber(
        {
          number: countNotToxin,
      
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
      );
    $('#source-count').animateNumber(
        {
          number: countSource,
      
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
      );
    $('#organism-count').animateNumber(
        {
          number: countOrganism,
      
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
      );
    $('#coleoptera-count').animateNumber(
        {
          number: countSpecies.get("Coleoptera"),
      
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
      );
    $('#diptera-count').animateNumber(
        {
          number: countSpecies.get("Diptera"),
      
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
      );
    $('#lepidoptera-count').animateNumber(
        {
          number: countSpecies.get("Lepidoptera"),
      
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
      );
    $('#rhabditida-count').animateNumber(
        {
          number: countSpecies.get("Rhabditida"),
      
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
      );

      initResearchChart();
      initFactorChart();
      initTargetChart();
});