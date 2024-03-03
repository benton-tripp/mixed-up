$(document).ready(function() {
    let selectedAnimals = [];

    $('.animal-btn').click(function() {
        const animal = $(this).data('animal');

        if ($(this).hasClass('selected')) {
            // Deselect the animal
            $(this).removeClass('selected');
            selectedAnimals = selectedAnimals.filter(item => item !== animal);
        } else if (selectedAnimals.length < 2) {
            // Select the animal
            $(this).addClass('selected');
            selectedAnimals.push(animal);
        }

        // Update hidden inputs based on the selected animals
        $('#animal1').val(selectedAnimals[0] || '');
        $('#animal2').val(selectedAnimals[1] || '');

        // Toggle the submit button based on the number of selections
        $('#submitBtn').prop('disabled', selectedAnimals.length !== 2);
    });

    $('#animalForm').submit(function() {
        // Show the loading overlay
        $('#loadingOverlay').show();
    });

    $('#resetBtn').click(function() {
        // Clear selections and reset the form
        selectedAnimals = [];
        $('.animal-btn').removeClass('selected');
        $('#animal1').val('');
        $('#animal2').val('');
        $('#submitBtn').prop('disabled', true);
    });
});
