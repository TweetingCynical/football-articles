const articles = "assets/js/articles.json";
const sourceButtons = $(".sourceButtons");
const storyCards = $(".news");
const sourceMapping = {
  mirror: "Mirror",
  manchestereveningnews: "Manchester Evening News",
  skysports: "Sky Sports",
  football365: "Football365",
};

const init = () => {
  fetch(articles)
    .then((response) => response.json())
    .then((data) => {
      showAllNews(data);
      console.log(data);
    })
    .catch((error) => {
      console.error("Error fetching JSON:", error);
    });
};

// Create all news articles
const showAllNews = (data) => {
  // Create four buttons for sources
  const allBtn = $("<h2>")
    .addClass("sourceButton tag rounded shadow-lg")
    .text("All")
    .click(() => toggleVisibility("All"));
  const menBtn = $("<h2>")
    .addClass("sourceButton manchestereveningnews rounded shadow-lg")
    .text("MEN")
    .click(() => toggleVisibility("manchestereveningnews"));
  const mirrorBtn = $("<h2>")
    .addClass("sourceButton mirror rounded shadow-lg")
    .text("Mirror")
    .click(() => toggleVisibility("mirror"));
  const skySportsBtn = $("<h2>")
    .addClass("sourceButton skysports rounded shadow-lg")
    .text("Sky Sports")
    .click(() => toggleVisibility("skysports"));
  const football365Btn = $("<h2>")
    .addClass("sourceButton football365 rounded shadow-lg")
    .text("Football 365")
    .click(() => toggleVisibility("football365"));
  sourceButtons.append(allBtn, menBtn, mirrorBtn, skySportsBtn, football365Btn);

  // Filter out objects with null or undefined 'headline' values
  const filteredData = data.filter(
    (element) => element.headline !== null && element.headline !== undefined
  );

  // Sort the filtered data by 'source' in descending order and then by 'date' in descending order
  const sortedData = filteredData.sort((a, b) => {
    // Sort by 'source' in descending order
    const sourceComparison = new Date(b.date) - new Date(a.date);

    // If 'source' values are the same, sort by 'date' in descending order
    if (sourceComparison === 0) {
      return b.source.localeCompare(a.source);
    }

    return sourceComparison;
  });

  sortedData.forEach((element) => {
    const { headline, tags, date, link, source, image, body } = element;
    const correctedHeadlineEnd = headline.endsWith("VIDEO")
      ? headline.slice(0, -5)
      : headline;
    const correctedHeadline = correctedHeadlineEnd.startsWith("opinion")
      ? correctedHeadlineEnd.slice(7)
      : correctedHeadlineEnd;
    const storyCard = $("<article>")
      .addClass("storyCard card p-3 m-3 shadow-lg rounded")
      .click(() => toggleBodyVisibility(bodyCard));
    const bodyCard = $("<section>").addClass("bodyCard p-2 m-2");
    body.forEach((paragraph, index) => {
      // Remove leading and trailing whitespace, including zero-width non-joiners
      const cleanedParagraph = paragraph
        .trim()
        .replace(/[\x00-\x1F\x7F-\x9F\u200B-\u200D\uFEFF]/g, "");

      const paragraphElement = $("<p>").text(`${cleanedParagraph}`);
      if (index === 0) {
        paragraphElement.addClass("subHeader");
      } else {
        paragraphElement.addClass("hidden");
      }

      // Check if the cleaned paragraph contains a single quote
      const quotePhrases = [
        '"',
        "“",
        "said: ",
        "continued: ",
        "added: ",
        "concluded: ",
      ];

      if (quotePhrases.some((phrase) => cleanedParagraph.includes(phrase))) {
        paragraphElement.addClass("quote");
      }

      // Check if the cleaned paragraph starts with a single quote
      bodyCard.append(paragraphElement);
    });
    const columnLeft = $("<div>").addClass("col-lg-8 col-md-8 col-sm-8");
    const headlineElement = $("<h2>")
      .addClass("headline")
      .text(`${correctedHeadline}`);
    const tagsElement = $("<div>").addClass("tags");
    tags.forEach((tag) => {
      const tagElement = $("<h5>")
        .addClass("tag rounded shadow-lg")
        .text(`${tag}`);
      tagsElement.append(tagElement);
    });
    const articleDate = $("<h5>")
      .addClass("date")
      .text(
        new Date(date).toLocaleDateString("en-US", {
          weekday: "long",
          day: "numeric",
          month: "long",
          year: "numeric",
          hour: "numeric",
          minute: "numeric",
          hour12: false, // Use 24-hour format
        })
      );
    const correctedSource = sourceMapping[source] || "Other";

    const articleSource = $("<a>")
      .addClass(`source ${source} shadow-lg rounded`)
      .attr("href", link)
      .attr("target", "_blank")
      .attr("rel", "noopener noreferrer")
      .text(`${correctedSource}`);
    columnLeft.append(headlineElement, articleSource, articleDate);
    const columnRight = $("<div>").addClass("col-lg-4 col-md-4 col-sm-4");
    const correctedImage = image == null ? "assets/images/default.jpeg" : image;

    const imageElement = $("<img>")
      .attr("src", correctedImage)
      .addClass("headlineImage shadow-lg rounded p-0 m-2");
    columnRight.append(imageElement);
    // Use Bootstrap row class to ensure columns sit side by side
    const row = $("<div>").addClass("row");
    row.append(columnLeft, columnRight);

    storyCard.append(row, tagsElement, bodyCard);
    storyCards.append(storyCard);
  });
};

const toggleBodyVisibility = (bodyCard) => {
  // Find all p elements (not the first one) within bodyCard and toggle the "hidden" class
  bodyCard.find("p:not(:first-child)").toggleClass("hidden");
};

const toggleVisibility = (selectedSource) => {
  storyCards.find(".storyCard").each((index, card) => {
    const source = $(card).find(".source").attr("class");
    const isMatch = source.includes(selectedSource);

    // Toggle visibility based on the selected source
    if (selectedSource === "All" || isMatch) {
      $(card).show(); // Show the storyCard
    } else {
      $(card).hide(); // Hide the storyCard
    }
  });

  // If a specific source button is clicked, also remove hidden class from all other source buttons
  sourceButtons.find("h2").each((index, button) => {
    if ($(button).text() !== selectedSource) {
      $(button).removeClass("hidden");
    }
  });
};

init();
