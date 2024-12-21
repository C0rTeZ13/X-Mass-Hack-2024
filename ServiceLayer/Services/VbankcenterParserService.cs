using System.Text.Json.Nodes;
using System.Text.Json;
using ServiceLayer.Models.Parsing;

namespace ServiceLayer.Services
{
    public class VbankcenterParserService
    {
       public async Task<CompanyInfo?> GetСompanyInfoAsync(string INN)
        {
            var client = new HttpClient();
            var request = new HttpRequestMessage(HttpMethod.Get, $"https://vbankcenter.ru/contragent/api/web/counterparty/filter?searchStr={INN}");
            var response = await client.SendAsync(request);
            string content = await response.Content.ReadAsStringAsync();
            FilterResponse? resp = JsonSerializer.Deserialize<FilterResponse>(content);
            if (resp == null) return null;
            string ogrn = resp?.content?.FirstOrDefault(c => c.inn.Contains(INN.ToString()))?.ogrn;
            if (ogrn == null) return null;


            request = new HttpRequestMessage(HttpMethod.Get, $"https://vbankcenter.ru/contragent/api/web/counterparty/ogrn/{ogrn}/details");
            response = await client.SendAsync(request);
            content = await response.Content.ReadAsStringAsync();
            DetailsResponse? info = JsonSerializer.Deserialize<DetailsResponse>(content);
            JsonNode? node = JsonNode.Parse(content);
            var empCountByYears = node?["employeeCountByYears"];
            int lastYear = DateTime.Now.Year-1;
            int? empCount = empCountByYears?[lastYear.ToString()]?.GetValue<int>();

            client = new HttpClient();
            request = new HttpRequestMessage(HttpMethod.Get, $"https://vbankcenter.ru/contragent/api/web/counterparty/inn/{INN}/finreport");
            response = await client.SendAsync(request);

            decimal? revenue = null;
            IEnumerable<Finreport>? finreports = JsonSerializer.Deserialize<IEnumerable<Finreport>>(response.Content.ReadAsStream());
            if (finreports != null && finreports.Any())
            {
                int? year = finreports?.Max(x => x.year);
                revenue = finreports?.First(r => r.year == year)?.revenue;
            }

            CompanyInfo report = new CompanyInfo()
            {
                INN = INN,
                RecommendedDealLimit = info?.recommendedDealLimit,
                ReliabilityRating = info?.reliabilityRating,
                Revenue = revenue,
                ActivityCode = info?.mainActivityType.code,
                EmemployeeCount = empCount
            };
            return report;
        }
    }
}
