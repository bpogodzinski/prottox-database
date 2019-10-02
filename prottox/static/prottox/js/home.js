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
          duration: 3000
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
          duration: 3000
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
          duration: 3000
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
          duration: 3000
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
          duration: 3000
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
          duration: 3000
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
          duration: 3000
        }
      );
});