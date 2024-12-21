using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ServiceLayer.Models.Exceptions;
using ServiceLayer.Services;


namespace API.Controllers
{
    [ApiController]
    [Route("[controller]")]
    [AllowAnonymous]
    public class ScoringController : ControllerBase
    {
        private readonly ScoringService _scoringService;
        private readonly XlsFileService _xlsFileService;
        public ScoringController(ScoringService scoringService, XlsFileService xlsFileService)
        {
            _scoringService = scoringService;
            _xlsFileService = xlsFileService;
        }

        [HttpPost]
        [ProducesResponseType(typeof(FileResult), 200)]
        public async Task<IActionResult> GetScoringResponceAsync(IFormFile file)
        {
            try
            {
                string filePath = await _xlsFileService.WriteXlsFile(file);
                await _scoringService.ComplementCompanyFile(filePath);
                await _scoringService.ExecuteScoring(filePath);
                string outPath = Path.ChangeExtension(Path.GetFileNameWithoutExtension(filePath)+"_result", Path.GetExtension(filePath));
                return new FileStreamResult(System.IO.File.OpenRead(filePath), "application/octet-stream") { FileDownloadName = outPath };
            }
            catch (ClientSideException ex)
            {
                return new ObjectResult(ex.Message) { StatusCode = 400 };
            }
        }
    }
}
