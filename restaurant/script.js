(function () {
  "use strict";

  var menu = [
    {
      name: "The Classic",
      description: "Beef patty, cheddar, lettuce, tomato, house sauce",
      price: "$9.50",
    },
    {
      name: "Bacon Smash",
      description: "Double patty, crispy bacon, caramelized onions, smoked gouda",
      price: "$12.00",
    },
    {
      name: "Veggie Delight",
      description: "Grilled portobello & black bean patty, avocado, chipotle mayo",
      price: "$10.00",
    },
    {
      name: "Spicy Jalapeño",
      description: "Beef patty, pepper jack, jalapeños, chipotle aioli",
      price: "$10.50",
    },
  ];

  // Each entry: days are 0 (Sunday) .. 6 (Saturday), open/close in 24h local time.
  var hours = [
    { label: "Monday – Thursday", days: [1, 2, 3, 4], open: 11, close: 21 },
    { label: "Friday – Saturday", days: [5, 6], open: 11, close: 22 },
    { label: "Sunday", days: [0], open: 12, close: 20 },
  ];

  function renderMenu() {
    var list = document.getElementById("menu-list");
    menu.forEach(function (item) {
      var li = document.createElement("li");

      var info = document.createElement("div");
      var name = document.createElement("p");
      name.className = "item-name";
      name.textContent = item.name;
      var description = document.createElement("p");
      description.className = "item-description";
      description.textContent = item.description;
      info.appendChild(name);
      info.appendChild(description);

      var price = document.createElement("span");
      price.className = "item-price";
      price.textContent = item.price;

      li.appendChild(info);
      li.appendChild(price);
      list.appendChild(li);
    });
  }

  function formatHour(hour) {
    var period = hour >= 12 ? "PM" : "AM";
    var displayHour = hour % 12;
    if (displayHour === 0) {
      displayHour = 12;
    }
    return displayHour + ":00 " + period;
  }

  function renderHours() {
    var list = document.getElementById("hours-list");
    hours.forEach(function (entry) {
      var li = document.createElement("li");

      var row = document.createElement("div");
      row.className = "hours-row";

      var day = document.createElement("span");
      day.textContent = entry.label;

      var time = document.createElement("span");
      time.textContent = formatHour(entry.open) + " – " + formatHour(entry.close);

      row.appendChild(day);
      row.appendChild(time);
      li.appendChild(row);
      list.appendChild(li);
    });
  }

  function renderOpenStatus() {
    var now = new Date();
    var day = now.getDay();
    var hour = now.getHours();

    var todaysHours = hours.find(function (entry) {
      return entry.days.indexOf(day) !== -1;
    });

    var statusEl = document.getElementById("open-status");
    var isOpen = !!todaysHours && hour >= todaysHours.open && hour < todaysHours.close;

    statusEl.textContent = isOpen ? "We're open right now!" : "We're closed right now.";
    statusEl.classList.add(isOpen ? "open" : "closed");
  }

  function renderFooter() {
    document.getElementById("footer-year").textContent =
      "© " + new Date().getFullYear() + " Riverside Burger Co. All rights reserved.";
  }

  document.addEventListener("DOMContentLoaded", function () {
    renderMenu();
    renderHours();
    renderOpenStatus();
    renderFooter();
  });
})();
