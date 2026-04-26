function testing() {
    const heading = document.querySelector("h1");
    if (heading.textContent === "HOME PAGE") {
    heading.textContent = "Changed by JavaScript!";
    } else {
    heading.textContent = "HOME PAGE";
}
}

let counter = 0;

function counterFunction() {
    counter++;
    document.querySelector("h2").textContent = "Counter: " + counter;

    if (counter % 5 === 0) {
        alert(`Count is now ${counter}!`);
    }
}

function confirmation(event){
    event.preventDefault();
    if (confirm("Are you sure you want to submit the order?")) {
        document.querySelector("form").submit();
    } else {
        alert("Order cancelled.");
    }
}
document.addEventListener("DOMContentLoaded", function() {
    document.querySelector('#submitButton').onclick = confirmation;
});

document.addEventListener("DOMContentLoaded", function() {
    document.querySelector('#counterButton').onclick = counterFunction;
});


document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#color-select').forEach(function(select) {
        select.addEventListener('change', function() {
            const selectedValue = this.value;
            if (selectedValue === 'selected') {
                this.style.backgroundColor = 'lightgreen';
            } else {
                this.style.backgroundColor = '';
                  }
        });
    });
});
