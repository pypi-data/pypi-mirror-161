import { BuildWebPage } from "./app.po";

describe("build-web App", () => {
    let page: BuildWebPage;

    beforeEach(() => {
        page = new BuildWebPage();
    });

    it("should display message saying app works", () => {
        page.navigateTo();
        expect(page.getParagraphText()).toEqual("app works!");
    });
});
