namespace ServiceLayer.Models.Parsing
{
    public class FilterResponse
    {
        public IEnumerable<FilterResponseItem> content { get; set; }
    }

    public class FilterResponseItem
    {
        public string ogrn { get; set; }
        public string inn { get; set; }
    }
}
