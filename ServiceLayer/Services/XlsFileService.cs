using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using ServiceLayer.Models;
using ServiceLayer.Models.Exceptions;
using System.IO;


namespace ServiceLayer.Services
{
    public class XlsFileService
    {
        private readonly string _fileStoragePath;

        public XlsFileService(IConfiguration configuration)
        {
            _fileStoragePath = configuration["FilesStorage"];
        }

        public async Task<string> WriteXlsFile(IFormFile file)
        {
            string extension = Path.GetExtension(file.FileName);
            if (extension != ".xlsx" && extension != ".xls") throw new ClientSideException("Invalid file format, supported formats: xlsx, xls");
            string path = Path.Combine(_fileStoragePath, file.FileName);
            using Stream fileStream = new FileStream(path, FileMode.Create);
            await file.CopyToAsync(fileStream);
            return path;
        }
    }
}
