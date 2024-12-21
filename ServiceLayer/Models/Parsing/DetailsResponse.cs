namespace ServiceLayer.Models.Parsing
{
    public class DetailsResponse
    {
        public int reliabilityRating { get; set; }
        public decimal recommendedDealLimit { get; set; }
        public MainActivityType mainActivityType { get; set; }
    }
    public class MainActivityType
    {
        public string code { get; set; }
    }
}
