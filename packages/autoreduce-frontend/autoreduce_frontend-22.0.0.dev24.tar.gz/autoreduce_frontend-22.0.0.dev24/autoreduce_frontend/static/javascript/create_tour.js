(function () {
    function setupTour(steps) {
        const tour = new Tour({
            steps: steps,
            backdrop: true,
            backdropPadding: 2,
            framework: 'bootstrap4',
        });

        const tourButton = $("#tour-btn");
        tourButton.click(function () {
            if (tour.ended()) {
                tour.restart();
            }
            tour.start();
        });
    }

    const init = function init() {
        document.getElementById('right_of_title').innerHTML = '<button class="btn btn-info btn-block" id="tour-btn">Take a tour</button>';
        setupTour(tourSteps);
    };

    init();
}());



