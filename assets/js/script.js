const articles = "assets/js/articles.json";
const storyCards = $(".news");
const sourceMapping = {
  mirror: "Mirror",
  manchestereveningnews: "Manchester Evening News",
  skysports: "Sky Sports",
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
    const bodyCard = $("<section>").addClass(
      "bodyCard card p-3 m-3 shadow-lg rounded hidden"
    );
    body.forEach((paragraph) => {
      const paragraphElement = $("<p>").addClass("hidden").text(`${paragraph}`);
      bodyCard.append(paragraphElement);
    });
    const columnLeft = $("<div>").addClass("col-lg-8 col-md-8 col-sm-8");
    const headlineElement = $("<h2>")
      .addClass("headline")
      .text(`${correctedHeadline}`);
    const tagsElement = $("<div>").addClass("tags");
    tags.forEach((tag) => {
      const tagElement = $("<h4>").addClass("tag shadow-lg").text(`${tag}`);
      tagsElement.append(tagElement);
    });
    const articleDate = $("<h4>")
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
    // const correctedSource =
    //   source == "mirror" ? "Mirror" : "Manchester Evening News";
    const correctedSource = sourceMapping[source] || "Other";

    // const sourceElement = $("<div>").addClass(`${source}`);
    const articleSource = $("<a>")
      .addClass(`source ${source} shadow-lg rounded`)
      .attr("href", link)
      .text(`${correctedSource}`);
    // sourceElement.append(articleSource);
    columnLeft.append(headlineElement, articleDate, articleSource);
    const columnRight = $("<div>").addClass("col-lg-4 col-md-4 col-sm-4");
    const correctedImage =
      image == null ? "../../assets/images/default.jpeg" : image;

    const imageElement = $("<img>")
      .attr("src", correctedImage)
      .addClass("headline-image shadow-lg rounded p-0 m-2");
    columnRight.append(imageElement);
    // Use Bootstrap row class to ensure columns sit side by side
    const row = $("<div>").addClass("row");
    row.append(columnLeft, columnRight);

    storyCard.append(row, tagsElement, bodyCard);
    storyCards.append(storyCard);
  });
};

const toggleBodyVisibility = (bodyCard) => {
  bodyCard.toggleClass("hidden");

  // Find all p elements within bodyCard and toggle the "hidden" class
  bodyCard.find("p").toggleClass("hidden");
};

init();
