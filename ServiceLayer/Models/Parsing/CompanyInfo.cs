namespace ServiceLayer.Models.Parsing
{
    public class CompanyInfo
    {
        public string INN { get; set; }
        public int? ReliabilityRating { get; set; }
        public decimal? RecommendedDealLimit { get; set; }
        public decimal? Revenue { get; set; }
        public string? ActivityCode { get; set; }
        public int? EmemployeeCount { get; set; }

        public override string ToString()
        {
            return $"{INN},{ReliabilityRating},{RecommendedDealLimit},{Revenue},{ActivityCode},{EmemployeeCount}";
        }
    }
}
